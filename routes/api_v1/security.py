"""
Security & Access Control API Endpoints
For API key management, rate limiting, and audit logging
"""

from flask import request, jsonify
from . import bp
from database import db
from models.security import ApiKey, ApiAccessLog
from utils.api_helpers import success_response, error_response, validation_error
from utils.auth import require_api_key, require_scope, validate_scopes
from datetime import datetime, timedelta
import secrets
import hashlib


@bp.route('/auth/api-keys', methods=['POST'])
@require_api_key
@require_scope('admin:security')
def create_api_key():
    """
    Generate a new API key for external access
    Key is generated once and shown only once - cannot be retrieved again
    Validates scopes against VALID_SCOPES before creation.
    """
    data = request.get_json()
    if not data:
        return validation_error('Request body required')

    if not data.get('name'):
        return validation_error('name is required')

    try:
        # Generate cryptographically secure key
        raw_key = secrets.token_hex(32)  # 64 hex characters
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        key_prefix = raw_key[:8]

        # Parse and validate scopes (Phase 5F)
        scopes_list = data.get('scopes', [])
        if isinstance(scopes_list, str):
            scopes_list = [s.strip() for s in scopes_list.split(',') if s.strip()]

        valid, invalid_scopes = validate_scopes(scopes_list)
        if not valid:
            return error_response(
                f'Invalid scopes: {", ".join(invalid_scopes)}',
                code='VALIDATION_ERROR',
                details={'invalid_scopes': invalid_scopes}
            )

        scopes_str = ','.join(scopes_list)

        # Parse rate limit (Phase 5D: 60/min for LOW, 120/min for MEDIUM/HIGH)
        rate_limit = data.get('rate_limit', 120)
        if not isinstance(rate_limit, int) or rate_limit < 1 or rate_limit > 10000:
            return validation_error('rate_limit must be an integer between 1 and 10000')

        # Parse expiration
        expires_at = None
        if data.get('expires_at'):
            try:
                expires_at = datetime.fromisoformat(data['expires_at'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return validation_error('expires_at must be in ISO datetime format')

        api_key = ApiKey(
            name=data['name'],
            key_hash=key_hash,
            key_prefix=key_prefix,
            scopes=scopes_str,
            rate_limit=rate_limit,
            is_active=True,
            expires_at=expires_at
        )
        db.session.add(api_key)
        db.session.commit()

        return success_response({
            'key_id': api_key.id,
            'name': api_key.name,
            'api_key': raw_key,  # Show ONLY ONCE
            'key_prefix': key_prefix + '****',
            'scopes': scopes_list,
            'rate_limit': rate_limit,
            'is_active': True,
            'created_at': api_key.created_at.isoformat(),
            'expires_at': api_key.expires_at.isoformat() if api_key.expires_at else None,
            'warning': 'This key is shown only once. Store it securely. You cannot retrieve it again.'
        }, message='API key created', status=201)

    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@bp.route('/auth/api-keys', methods=['GET'])
@require_api_key
@require_scope('admin:security')
def list_api_keys():
    """
    List all API keys (showing only prefix, never the full key)
    """
    keys = ApiKey.query.order_by(ApiKey.created_at.desc()).all()

    return success_response({
        'keys': [k.to_dict() for k in keys],
        'total_count': len(keys),
        'active_count': sum(1 for k in keys if k.is_active),
        'note': 'Key prefixes shown for identification. Full keys cannot be retrieved once created.'
    })


@bp.route('/auth/api-keys/<int:key_id>', methods=['DELETE'])
@require_api_key
@require_scope('admin:security')
def revoke_api_key(key_id):
    """
    Revoke an API key (soft delete - marks as inactive)
    """
    api_key = ApiKey.query.get(key_id)
    if not api_key:
        return error_response(f'API key {key_id} not found', code='NOT_FOUND', status=404)

    try:
        api_key.is_active = False
        db.session.commit()
        return success_response(
            {'key_id': key_id, 'status': 'revoked'},
            message='API key revoked'
        )
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@bp.route('/auth/rate-limit', methods=['GET'])
@require_api_key
@require_scope('read:security')
def get_rate_limit_status():
    """
    Get current rate limit status
    Returns requests made in last 60 seconds and remaining quota
    Uses ApiAccessLog for accurate per-key tracking.
    """
    from flask import g

    # Determine which key to check rate limit for
    api_key = getattr(g, 'api_key', None)

    sixty_seconds_ago = datetime.utcnow() - timedelta(seconds=60)

    if api_key:
        # Per-key rate limit status
        request_count = ApiAccessLog.query.filter(
            ApiAccessLog.key_id == api_key.id,
            ApiAccessLog.timestamp >= sixty_seconds_ago
        ).count()
    else:
        # Global rate limit status (web user)
        request_count = ApiAccessLog.query.filter(
            ApiAccessLog.timestamp >= sixty_seconds_ago
        ).count()

    # Rate limit from the key itself (Phase 5D enforcement)
    limit_per_minute = api_key.rate_limit if api_key else 120
    remaining = max(0, limit_per_minute - request_count)
    reset_at = datetime.utcnow() + timedelta(seconds=60)

    return success_response({
        'requests_last_minute': request_count,
        'limit': limit_per_minute,
        'remaining': remaining,
        'reset_at': reset_at.isoformat(),
        'enforcement': 'active',
        'key_prefix': api_key.key_prefix + '****' if api_key else None
    })


# ============================================================================
# AUDIT LOG ENDPOINT — Phase 5C
# ============================================================================

@bp.route('/auth/audit-log', methods=['GET'])
@require_api_key
@require_scope('admin:security')
def get_audit_log():
    """
    GET /api/v1/auth/audit-log
    Query API access logs for security review.

    Query params:
    - key_id: Filter by API key ID (optional)
    - endpoint: Filter by endpoint path (optional, partial match)
    - method: Filter by HTTP method (optional)
    - status_code: Filter by status code (optional)
    - since: ISO datetime to filter from (optional, default: last 24 hours)
    - until: ISO datetime to filter to (optional)
    - page: Page number (default: 1)
    - per_page: Items per page (default: 50, max: 200)
    """
    try:
        # Parse query parameters
        key_id = request.args.get('key_id', type=int)
        endpoint_filter = request.args.get('endpoint', '').strip()
        method_filter = request.args.get('method', '').strip().upper()
        status_code = request.args.get('status_code', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 200)

        # Parse date range
        since_str = request.args.get('since', '').strip()
        until_str = request.args.get('until', '').strip()

        if since_str:
            try:
                since = datetime.fromisoformat(since_str.replace('Z', '+00:00'))
            except ValueError:
                return validation_error('since must be in ISO datetime format')
        else:
            since = datetime.utcnow() - timedelta(hours=24)

        if until_str:
            try:
                until = datetime.fromisoformat(until_str.replace('Z', '+00:00'))
            except ValueError:
                return validation_error('until must be in ISO datetime format')
        else:
            until = None

        # Build query
        query = ApiAccessLog.query.filter(ApiAccessLog.timestamp >= since)

        if until:
            query = query.filter(ApiAccessLog.timestamp <= until)
        if key_id:
            query = query.filter(ApiAccessLog.key_id == key_id)
        if endpoint_filter:
            query = query.filter(ApiAccessLog.endpoint.like(f'%{endpoint_filter}%'))
        if method_filter:
            query = query.filter(ApiAccessLog.method == method_filter)
        if status_code:
            query = query.filter(ApiAccessLog.status_code == status_code)

        # Order and paginate
        query = query.order_by(ApiAccessLog.timestamp.desc())
        total = query.count()
        logs = query.offset((page - 1) * per_page).limit(per_page).all()

        pages = (total + per_page - 1) // per_page

        return success_response({
            'logs': [log.to_dict() for log in logs],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': pages,
                'has_next': page < pages,
                'has_prev': page > 1
            }
        })

    except Exception as e:
        return error_response(str(e))
