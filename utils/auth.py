"""
Authentication & Authorization Decorators
Provides require_api_key and require_scope decorators for API endpoint protection.

Usage:
    from utils.auth import require_api_key, require_scope

    @bp.route('/diary/entries', methods=['GET'])
    @require_api_key
    @require_scope('read:diary')
    def get_diary_entries():
        ...

Bypass: Web browser requests (no X-API-Key or Authorization header) are passed
through without authentication, so the existing web UI continues to work.
"""

from functools import wraps
from flask import request, g, jsonify
from datetime import datetime, timedelta
import hashlib

from utils.api_helpers import error_response, UNAUTHORIZED, FORBIDDEN


# ============================================================================
# VALID SCOPES — Phase 5F
# All 37 scopes used across the 20 API route files
# ============================================================================

VALID_SCOPES = [
    # -- Read scopes (21) --
    'read:diary',
    'read:analytics',
    'read:export',
    'read:chat',
    'read:compendium',
    'read:foods',
    'read:recipes',
    'read:search',
    'read:fodmap',
    'read:usda',
    'read:ausnut',
    'read:education',
    'read:help',
    'read:settings',
    'read:webhooks',
    'read:gamification',
    'read:reintroduction',
    'read:notifications',
    'read:integrations',
    'read:billing',
    'read:security',
    # multi_user — no read scope (admin only, uses admin:users)

    # -- Write scopes (11) --
    'write:diary',
    'write:foods',
    'write:recipes',
    'write:chat',
    'write:webhooks',
    'write:help',
    'write:education',
    'write:gamification',
    'write:reintroduction',
    'write:notifications',
    'write:integrations',
    # billing — no write scope (inbound webhook only, signature-verified)
    # search — no write scope (read-only)

    # -- Special scopes (5) --
    'stream:realtime',
    'admin:backup',
    'admin:settings',
    'admin:security',
    'admin:users',
]
# Total: 37 scopes (21 read + 11 write + 5 special)


def validate_scopes(scopes_list):
    """
    Validate that all scopes in a list are recognized.
    Returns (valid, invalid_scopes) tuple.
    """
    if not scopes_list:
        return True, []
    invalid = [s for s in scopes_list if s not in VALID_SCOPES]
    return len(invalid) == 0, invalid


# ============================================================================
# DECORATORS — Phase 5A
# ============================================================================

def require_api_key(f):
    """
    Decorator that enforces API key authentication.

    - Reads X-API-Key header (or Authorization: Bearer <key>)
    - Hashes incoming key with SHA-256 and looks up ApiKey by key_hash
    - Rejects if: key not found, is_active=False, expires_at has passed
    - Updates last_used timestamp on successful validation
    - Stores validated ApiKey on g.api_key for downstream use
    - Returns 401 UNAUTHORIZED with standard error response on failure
    - Bypass: Skip auth for web browser requests (no API key header = web user)
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Extract API key from headers
        api_key_value = request.headers.get('X-API-Key', '').strip()

        # Fallback: Authorization: Bearer <key>
        if not api_key_value:
            auth_header = request.headers.get('Authorization', '').strip()
            if auth_header.startswith('Bearer '):
                api_key_value = auth_header[7:].strip()

        # Bypass: No API key header = web browser user, allow through
        if not api_key_value:
            g.api_key = None
            return f(*args, **kwargs)

        # Hash the incoming key and look up
        from models.security import ApiKey
        from database import db

        key_hash = hashlib.sha256(api_key_value.encode()).hexdigest()
        api_key = ApiKey.query.filter_by(key_hash=key_hash).first()

        # Key not found
        if not api_key:
            _log_failed_access(request, 'invalid_key')
            return error_response(
                'Invalid API key',
                code=UNAUTHORIZED
            )

        # Key is revoked/inactive
        if not api_key.is_active:
            _log_failed_access(request, 'revoked_key', api_key.id)
            return error_response(
                'API key has been revoked',
                code=UNAUTHORIZED
            )

        # Key has expired
        if api_key.expires_at and api_key.expires_at < datetime.utcnow():
            _log_failed_access(request, 'expired_key', api_key.id)
            return error_response(
                'API key has expired',
                code=UNAUTHORIZED
            )

        # Valid key — update last_used and store on g
        api_key.last_used = datetime.utcnow()
        db.session.commit()
        g.api_key = api_key

        # Rate limiting (Phase 5D) — counter-based per API key
        rate_limit_val = api_key.rate_limit or 120
        sixty_seconds_ago = datetime.utcnow() - timedelta(seconds=60)
        from models.security import ApiAccessLog
        request_count = ApiAccessLog.query.filter(
            ApiAccessLog.key_id == api_key.id,
            ApiAccessLog.timestamp >= sixty_seconds_ago
        ).count()

        if request_count >= rate_limit_val:
            _log_failed_access(request, 'rate_limited', api_key.id)
            response = jsonify({
                'status': 'error',
                'message': 'Rate limit exceeded',
                'code': 'TOO_MANY_REQUESTS',
                'details': {
                    'limit': rate_limit_val,
                    'requests': request_count,
                    'retry_after': 60,
                    'key_prefix': api_key.key_prefix + '****'
                }
            })
            response.status_code = 429
            response.headers['Retry-After'] = '60'
            return response

        # Log successful access (Phase 5C audit logging)
        _log_successful_access(request, api_key)

        return f(*args, **kwargs)

    return decorated


def require_scope(scope_string):
    """
    Decorator that enforces scope-based authorization.

    Takes scope like 'read:diary' or 'write:recipes'.
    Checks g.api_key.scopes (CSV) contains the required scope.
    Returns 403 FORBIDDEN if scope missing.
    Must be used AFTER @require_api_key.

    If g.api_key is None (web browser bypass), scope check is skipped.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # If no API key (web browser bypass), skip scope check
            api_key = getattr(g, 'api_key', None)
            if api_key is None:
                return f(*args, **kwargs)

            # Parse scopes from the API key's CSV string
            key_scopes = [s.strip() for s in (api_key.scopes or '').split(',') if s.strip()]

            # Check if required scope is present
            if scope_string not in key_scopes:
                return error_response(
                    f'Insufficient permissions. Required scope: {scope_string}',
                    code=FORBIDDEN,
                    details={
                        'required_scope': scope_string,
                        'key_prefix': api_key.key_prefix + '****'
                    }
                )

            return f(*args, **kwargs)

        return decorated
    return decorator


# ============================================================================
# AUDIT LOGGING HELPERS — Phase 5C
# ============================================================================

def _log_successful_access(req, api_key):
    """Log a successful API access to the audit log."""
    try:
        from models.security import ApiAccessLog
        from database import db

        log = ApiAccessLog(
            key_id=api_key.id,
            endpoint=req.path,
            method=req.method,
            status_code=200,  # Will be updated by after_request if needed
            ip_address=req.remote_addr or 'unknown'
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        # Don't fail the main request if audit logging fails
        pass


def _log_failed_access(req, reason, key_id=None):
    """Log a failed API access attempt to the audit log."""
    try:
        from models.security import ApiAccessLog
        from database import db

        status_map = {
            'invalid_key': 401,
            'revoked_key': 401,
            'expired_key': 401,
            'missing_scope': 403,
        }

        log = ApiAccessLog(
            key_id=key_id,
            endpoint=req.path,
            method=req.method,
            status_code=status_map.get(reason, 401),
            ip_address=req.remote_addr or 'unknown'
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        # Don't fail the main request if audit logging fails
        pass
