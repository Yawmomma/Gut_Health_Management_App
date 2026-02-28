"""
Tests for security API endpoints.
Covers: API key CRUD, rate limit status, audit log query.
"""

import pytest
from datetime import datetime, timedelta


class TestCreateApiKey:
    """Tests for POST /api/v1/auth/api-keys."""

    def test_create_key_success(self, client, admin_key, db_session):
        """Should create a new API key and return it once."""
        raw_key, _ = admin_key
        resp = client.post('/api/v1/auth/api-keys',
                           headers={'X-API-Key': raw_key},
                           json={
                               'name': 'New Test Key',
                               'scopes': ['read:diary', 'read:analytics'],
                               'rate_limit': 60,
                           })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['data']['api_key'] is not None
        assert len(data['data']['api_key']) == 64  # hex(32 bytes)
        assert data['data']['name'] == 'New Test Key'
        assert 'warning' in data['data']

        # Cleanup
        from models.security import ApiKey, ApiAccessLog
        created = ApiKey.query.get(data['data']['key_id'])
        if created:
            ApiAccessLog.query.filter_by(key_id=created.id).delete()
            db_session.delete(created)
            db_session.commit()

    def test_create_key_requires_name(self, client, admin_key):
        """Should reject key creation without a name."""
        raw_key, _ = admin_key
        resp = client.post('/api/v1/auth/api-keys',
                           headers={'X-API-Key': raw_key},
                           json={'scopes': ['read:diary']})
        assert resp.status_code == 400

    def test_create_key_validates_scopes(self, client, admin_key):
        """Should reject unknown scopes."""
        raw_key, _ = admin_key
        resp = client.post('/api/v1/auth/api-keys',
                           headers={'X-API-Key': raw_key},
                           json={
                               'name': 'Bad Scopes Key',
                               'scopes': ['read:diary', 'write:unicorns'],
                           })
        # Should return an error for invalid scope
        data = resp.get_json()
        assert 'unicorns' in str(data)

    def test_create_key_requires_admin_scope(self, client, api_key):
        """Non-admin key should not be able to create new keys."""
        raw_key, _ = api_key  # Only has read scopes
        resp = client.post('/api/v1/auth/api-keys',
                           headers={'X-API-Key': raw_key},
                           json={'name': 'Sneaky Key', 'scopes': ['read:diary']})
        assert resp.status_code == 403

    def test_create_key_with_expiry(self, client, admin_key, db_session):
        """Should accept an expires_at datetime."""
        raw_key, _ = admin_key
        future = (datetime.utcnow() + timedelta(days=90)).isoformat()
        resp = client.post('/api/v1/auth/api-keys',
                           headers={'X-API-Key': raw_key},
                           json={
                               'name': 'Expiring Key',
                               'scopes': ['read:diary'],
                               'expires_at': future,
                           })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['data']['expires_at'] is not None

        # Cleanup
        from models.security import ApiKey, ApiAccessLog
        created = ApiKey.query.get(data['data']['key_id'])
        if created:
            ApiAccessLog.query.filter_by(key_id=created.id).delete()
            db_session.delete(created)
            db_session.commit()

    def test_create_key_scopes_as_csv_string(self, client, admin_key, db_session):
        """Should accept scopes as a comma-separated string."""
        raw_key, _ = admin_key
        resp = client.post('/api/v1/auth/api-keys',
                           headers={'X-API-Key': raw_key},
                           json={
                               'name': 'CSV Scopes Key',
                               'scopes': 'read:diary,read:analytics',
                           })
        assert resp.status_code == 201

        # Cleanup
        data = resp.get_json()
        from models.security import ApiKey, ApiAccessLog
        created = ApiKey.query.get(data['data']['key_id'])
        if created:
            ApiAccessLog.query.filter_by(key_id=created.id).delete()
            db_session.delete(created)
            db_session.commit()


class TestListApiKeys:
    """Tests for GET /api/v1/auth/api-keys."""

    def test_list_keys_returns_all(self, client, admin_key):
        """Should return all API keys (masked)."""
        raw_key, _ = admin_key
        resp = client.get('/api/v1/auth/api-keys',
                          headers={'X-API-Key': raw_key})
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'keys' in data['data']
        assert data['data']['total_count'] >= 1

    def test_list_keys_masks_values(self, client, admin_key):
        """Listed keys should show prefixes, never full keys."""
        raw_key, _ = admin_key
        resp = client.get('/api/v1/auth/api-keys',
                          headers={'X-API-Key': raw_key})
        data = resp.get_json()
        for key in data['data']['keys']:
            assert key['key_prefix'].endswith('****')
            assert 'key_hash' not in key


class TestRevokeApiKey:
    """Tests for DELETE /api/v1/auth/api-keys/<id>."""

    def test_revoke_key(self, client, admin_key, db_session):
        """Should soft-delete (deactivate) the key."""
        raw_admin, _ = admin_key
        from tests.conftest import _create_api_key

        # Create a key to revoke
        _, target_key = _create_api_key(db_session, name='To Revoke')

        resp = client.delete(f'/api/v1/auth/api-keys/{target_key.id}',
                             headers={'X-API-Key': raw_admin})
        assert resp.status_code == 200

        db_session.refresh(target_key)
        assert target_key.is_active is False

        # Cleanup
        from models.security import ApiAccessLog
        ApiAccessLog.query.filter_by(key_id=target_key.id).delete()
        db_session.delete(target_key)
        db_session.commit()

    def test_revoke_nonexistent_key(self, client, admin_key):
        """Should return 404 for nonexistent key ID."""
        raw_key, _ = admin_key
        resp = client.delete('/api/v1/auth/api-keys/99999',
                             headers={'X-API-Key': raw_key})
        assert resp.status_code == 404


class TestRateLimitStatus:
    """Tests for GET /api/v1/auth/rate-limit."""

    def test_rate_limit_status(self, app, client, db_session):
        """Should return current rate limit status for the key."""
        from tests.conftest import _create_api_key
        from models.security import ApiAccessLog

        raw_key, key_obj = _create_api_key(
            db_session, scopes='read:security,read:fodmap'
        )
        resp = client.get('/api/v1/auth/rate-limit',
                          headers={'X-API-Key': raw_key})
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'limit' in data['data']
        assert 'remaining' in data['data']
        assert 'requests_last_minute' in data['data']
        assert data['data']['enforcement'] == 'active'

        # Cleanup
        ApiAccessLog.query.filter_by(key_id=key_obj.id).delete()
        db_session.delete(key_obj)
        db_session.commit()

    def test_rate_limit_web_bypass(self, client):
        """Web browser should see rate limit status without auth."""
        resp = client.get('/api/v1/auth/rate-limit')
        assert resp.status_code == 200


class TestAuditLogEndpoint:
    """Tests for GET /api/v1/auth/audit-log."""

    def test_audit_log_returns_entries(self, client, admin_key):
        """Should return paginated audit log entries."""
        raw_key, _ = admin_key

        # Make a request to generate a log entry
        client.get('/api/v1/fodmap/categories',
                    headers={'X-API-Key': raw_key})

        resp = client.get('/api/v1/auth/audit-log',
                          headers={'X-API-Key': raw_key})
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'logs' in data['data']
        assert 'pagination' in data['data']
        assert data['data']['pagination']['total'] >= 1

    def test_audit_log_filter_by_method(self, client, admin_key):
        """Should filter logs by HTTP method."""
        raw_key, _ = admin_key
        resp = client.get('/api/v1/auth/audit-log?method=GET',
                          headers={'X-API-Key': raw_key})
        assert resp.status_code == 200
        data = resp.get_json()
        for log in data['data']['logs']:
            assert log['method'] == 'GET'

    def test_audit_log_requires_admin(self, client, api_key):
        """Non-admin key should not access audit logs."""
        raw_key, _ = api_key
        resp = client.get('/api/v1/auth/audit-log',
                          headers={'X-API-Key': raw_key})
        assert resp.status_code == 403

    def test_audit_log_pagination(self, client, admin_key):
        """Should respect per_page parameter."""
        raw_key, _ = admin_key
        resp = client.get('/api/v1/auth/audit-log?per_page=5',
                          headers={'X-API-Key': raw_key})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['data']['pagination']['per_page'] == 5
        assert len(data['data']['logs']) <= 5
