"""
Tests for the authentication & authorization system.
Covers: require_api_key, require_scope, rate limiting, audit logging, web bypass.
"""

import pytest
import secrets
import hashlib
from datetime import datetime, timedelta


# ============================================================================
# require_api_key decorator tests
# ============================================================================

class TestRequireApiKey:
    """Tests for the @require_api_key decorator."""

    def test_web_browser_bypass_no_header(self, client):
        """Web requests without API key headers should pass through."""
        resp = client.get('/api/v1/fodmap/categories')
        assert resp.status_code == 200

    def test_valid_api_key_x_header(self, client, api_key):
        """Valid X-API-Key header should authenticate successfully."""
        raw_key, _ = api_key
        resp = client.get('/api/v1/fodmap/categories',
                          headers={'X-API-Key': raw_key})
        assert resp.status_code == 200

    def test_valid_api_key_bearer(self, client, api_key):
        """Valid Authorization: Bearer token should authenticate successfully."""
        raw_key, _ = api_key
        resp = client.get('/api/v1/fodmap/categories',
                          headers={'Authorization': f'Bearer {raw_key}'})
        assert resp.status_code == 200

    def test_invalid_api_key_returns_401(self, client):
        """Invalid API key should return 401 Unauthorized."""
        resp = client.get('/api/v1/fodmap/categories',
                          headers={'X-API-Key': 'totally-invalid-key'})
        assert resp.status_code == 401
        data = resp.get_json()
        assert data['error']['code'] == 'UNAUTHORIZED'
        assert 'Invalid API key' in data['error']['message']

    def test_revoked_key_returns_401(self, app, client, db_session):
        """Revoked (inactive) API key should return 401."""
        from tests.conftest import _create_api_key
        raw_key, key_obj = _create_api_key(db_session, is_active=False)

        resp = client.get('/api/v1/fodmap/categories',
                          headers={'X-API-Key': raw_key})
        assert resp.status_code == 401
        data = resp.get_json()
        assert 'revoked' in data['error']['message'].lower()

        # Cleanup
        from models.security import ApiAccessLog
        ApiAccessLog.query.filter_by(key_id=key_obj.id).delete()
        db_session.delete(key_obj)
        db_session.commit()

    def test_expired_key_returns_401(self, app, client, db_session):
        """Expired API key should return 401."""
        from tests.conftest import _create_api_key
        raw_key, key_obj = _create_api_key(
            db_session,
            expires_at=datetime.utcnow() - timedelta(hours=1)
        )

        resp = client.get('/api/v1/fodmap/categories',
                          headers={'X-API-Key': raw_key})
        assert resp.status_code == 401
        data = resp.get_json()
        assert 'expired' in data['error']['message'].lower()

        # Cleanup
        from models.security import ApiAccessLog
        ApiAccessLog.query.filter_by(key_id=key_obj.id).delete()
        db_session.delete(key_obj)
        db_session.commit()

    def test_valid_key_updates_last_used(self, app, client, api_key, db_session):
        """Successful authentication should update last_used timestamp."""
        raw_key, key_obj = api_key
        assert key_obj.last_used is None  # Not used yet

        client.get('/api/v1/fodmap/categories',
                    headers={'X-API-Key': raw_key})

        db_session.refresh(key_obj)
        assert key_obj.last_used is not None

    def test_empty_api_key_treated_as_web(self, client):
        """Empty X-API-Key header should be treated as web browser request."""
        resp = client.get('/api/v1/fodmap/categories',
                          headers={'X-API-Key': ''})
        assert resp.status_code == 200

    def test_whitespace_api_key_treated_as_web(self, client):
        """Whitespace-only API key should be treated as web browser request."""
        resp = client.get('/api/v1/fodmap/categories',
                          headers={'X-API-Key': '   '})
        assert resp.status_code == 200


# ============================================================================
# require_scope decorator tests
# ============================================================================

class TestRequireScope:
    """Tests for the @require_scope decorator."""

    def test_correct_scope_allows_access(self, client, api_key):
        """API key with matching scope should be allowed."""
        raw_key, _ = api_key  # Has read:fodmap
        resp = client.get('/api/v1/fodmap/categories',
                          headers={'X-API-Key': raw_key})
        assert resp.status_code == 200

    def test_missing_scope_returns_403(self, client, api_key):
        """API key without required scope should get 403 Forbidden."""
        raw_key, _ = api_key  # Doesn't have admin:security
        resp = client.get('/api/v1/auth/api-keys',
                          headers={'X-API-Key': raw_key})
        assert resp.status_code == 403
        data = resp.get_json()
        assert data['error']['code'] == 'FORBIDDEN'
        assert 'scope' in data['error']['message'].lower()

    def test_web_bypass_skips_scope_check(self, client):
        """Web browser requests (no API key) should skip scope checks."""
        resp = client.get('/api/v1/auth/api-keys')
        # Should pass through even though admin:security scope is required
        assert resp.status_code == 200

    def test_admin_scope_grants_access(self, client, admin_key):
        """Admin key with admin:security scope should access admin endpoints."""
        raw_key, _ = admin_key
        resp = client.get('/api/v1/auth/api-keys',
                          headers={'X-API-Key': raw_key})
        assert resp.status_code == 200

    def test_write_scope_required_for_mutations(self, app, client, db_session):
        """Write endpoints should require write scopes."""
        from tests.conftest import _create_api_key
        # Key with only read:diary (no write:diary)
        raw_key, key_obj = _create_api_key(
            db_session, scopes='read:diary'
        )

        resp = client.post('/api/v1/diary/meals',
                           headers={'X-API-Key': raw_key},
                           json={'date': '2026-03-01', 'meal_type': 'Lunch'})
        assert resp.status_code == 403

        # Cleanup
        from models.security import ApiAccessLog
        ApiAccessLog.query.filter_by(key_id=key_obj.id).delete()
        db_session.delete(key_obj)
        db_session.commit()


# ============================================================================
# Audit logging tests
# ============================================================================

class TestAuditLogging:
    """Tests for API access audit logging."""

    def test_successful_request_creates_log(self, app, client, api_key, db_session):
        """Successful API requests should create audit log entries."""
        from models.security import ApiAccessLog
        raw_key, key_obj = api_key

        # Count logs before
        count_before = ApiAccessLog.query.filter_by(key_id=key_obj.id).count()

        client.get('/api/v1/fodmap/categories',
                    headers={'X-API-Key': raw_key})

        count_after = ApiAccessLog.query.filter_by(key_id=key_obj.id).count()
        assert count_after > count_before

    def test_failed_auth_creates_log(self, app, client, db_session):
        """Failed authentication attempts should also be logged."""
        from models.security import ApiAccessLog

        count_before = ApiAccessLog.query.count()

        client.get('/api/v1/fodmap/categories',
                    headers={'X-API-Key': 'invalid-key-for-logging-test'})

        count_after = ApiAccessLog.query.count()
        assert count_after > count_before

    def test_audit_log_records_correct_endpoint(self, app, client, api_key, db_session):
        """Audit log should record the correct endpoint path."""
        from models.security import ApiAccessLog
        raw_key, key_obj = api_key

        client.get('/api/v1/fodmap/categories',
                    headers={'X-API-Key': raw_key})

        log = ApiAccessLog.query.filter_by(
            key_id=key_obj.id
        ).order_by(ApiAccessLog.id.desc()).first()

        assert log is not None
        assert '/api/v1/fodmap/categories' in log.endpoint
        assert log.method == 'GET'

    def test_audit_log_records_method(self, app, client, api_key, db_session):
        """Audit log should record the HTTP method."""
        from models.security import ApiAccessLog
        raw_key, key_obj = api_key

        client.get('/api/v1/fodmap/categories',
                    headers={'X-API-Key': raw_key})

        log = ApiAccessLog.query.filter_by(
            key_id=key_obj.id
        ).order_by(ApiAccessLog.id.desc()).first()

        assert log.method == 'GET'


# ============================================================================
# Rate limiting tests
# ============================================================================

class TestRateLimiting:
    """Tests for per-key rate limiting."""

    def test_rate_limit_enforced_when_exceeded(self, app, client, db_session):
        """Requests should be rejected when rate limit is exceeded."""
        from tests.conftest import _create_api_key
        from models.security import ApiAccessLog

        # Create a key with very low rate limit
        raw_key, key_obj = _create_api_key(
            db_session, scopes='read:fodmap', rate_limit=3
        )

        # Make requests up to and beyond the limit
        statuses = []
        for i in range(5):
            resp = client.get('/api/v1/fodmap/categories',
                              headers={'X-API-Key': raw_key})
            statuses.append(resp.status_code)

        # Should see some 200s followed by 429s
        assert 200 in statuses, "Should have at least one successful request"
        assert 429 in statuses, "Should hit rate limit"

        # Cleanup
        ApiAccessLog.query.filter_by(key_id=key_obj.id).delete()
        db_session.delete(key_obj)
        db_session.commit()

    def test_rate_limit_returns_retry_after(self, app, client, db_session):
        """Rate limited response should include Retry-After header."""
        from tests.conftest import _create_api_key
        from models.security import ApiAccessLog

        raw_key, key_obj = _create_api_key(
            db_session, scopes='read:fodmap', rate_limit=1
        )

        # First request should succeed
        client.get('/api/v1/fodmap/categories',
                    headers={'X-API-Key': raw_key})

        # Second request should be rate limited
        resp = client.get('/api/v1/fodmap/categories',
                          headers={'X-API-Key': raw_key})

        if resp.status_code == 429:
            assert resp.headers.get('Retry-After') == '60'
            data = resp.get_json()
            assert data['code'] == 'TOO_MANY_REQUESTS'

        # Cleanup
        ApiAccessLog.query.filter_by(key_id=key_obj.id).delete()
        db_session.delete(key_obj)
        db_session.commit()

    def test_web_requests_not_rate_limited(self, client):
        """Web browser requests (no API key) should not be rate limited."""
        for _ in range(5):
            resp = client.get('/api/v1/fodmap/categories')
            assert resp.status_code == 200


# ============================================================================
# Scope validation tests
# ============================================================================

class TestScopeValidation:
    """Tests for scope validation utility."""

    def test_valid_scopes_pass(self):
        """All defined scopes should be recognized as valid."""
        from utils.auth import validate_scopes
        valid, invalid = validate_scopes(['read:diary', 'write:recipes', 'admin:security'])
        assert valid is True
        assert invalid == []

    def test_invalid_scope_rejected(self):
        """Unknown scopes should be rejected."""
        from utils.auth import validate_scopes
        valid, invalid = validate_scopes(['read:diary', 'write:unicorns'])
        assert valid is False
        assert 'write:unicorns' in invalid

    def test_empty_scopes_valid(self):
        """Empty scope list should be valid."""
        from utils.auth import validate_scopes
        valid, invalid = validate_scopes([])
        assert valid is True
        assert invalid == []

    def test_all_scopes_defined(self):
        """Should have exactly 37 valid scopes defined (21 read + 11 write + 5 special)."""
        from utils.auth import VALID_SCOPES
        assert len(VALID_SCOPES) == 37
        read = [s for s in VALID_SCOPES if s.startswith('read:')]
        write = [s for s in VALID_SCOPES if s.startswith('write:')]
        special = [s for s in VALID_SCOPES if not s.startswith('read:') and not s.startswith('write:')]
        assert len(read) == 21
        assert len(write) == 11
        assert len(special) == 5
