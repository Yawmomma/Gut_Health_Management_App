"""
Tests for model serialization (to_dict methods).
Covers: ApiKey, ApiAccessLog models.
"""

import pytest
import secrets
import hashlib
from datetime import datetime, timedelta


class TestApiKeyModel:
    """Tests for the ApiKey model."""

    def test_to_dict_masks_key(self, app, db_session):
        """to_dict should show key_prefix + mask, never the full key."""
        from models.security import ApiKey

        raw_key = secrets.token_hex(32)
        key = ApiKey(
            name='Test',
            key_hash=hashlib.sha256(raw_key.encode()).hexdigest(),
            key_prefix=raw_key[:8],
            scopes='read:diary',
            is_active=True,
        )
        db_session.add(key)
        db_session.commit()

        d = key.to_dict()
        assert d['key_prefix'].endswith('****')
        assert d['key_prefix'] == raw_key[:8] + '****'
        assert 'key_hash' not in d
        assert raw_key not in str(d)

        db_session.delete(key)
        db_session.commit()

    def test_to_dict_parses_scopes_as_list(self, app, db_session):
        """Scopes CSV should be returned as a list."""
        from models.security import ApiKey

        raw_key = secrets.token_hex(32)
        key = ApiKey(
            name='Test',
            key_hash=hashlib.sha256(raw_key.encode()).hexdigest(),
            key_prefix=raw_key[:8],
            scopes='read:diary,write:diary,read:analytics',
            is_active=True,
        )
        db_session.add(key)
        db_session.commit()

        d = key.to_dict()
        assert isinstance(d['scopes'], list)
        assert len(d['scopes']) == 3
        assert 'read:diary' in d['scopes']

        db_session.delete(key)
        db_session.commit()

    def test_to_dict_empty_scopes(self, app, db_session):
        """Empty scopes should return empty list."""
        from models.security import ApiKey

        raw_key = secrets.token_hex(32)
        key = ApiKey(
            name='Test',
            key_hash=hashlib.sha256(raw_key.encode()).hexdigest(),
            key_prefix=raw_key[:8],
            scopes='',
            is_active=True,
        )
        db_session.add(key)
        db_session.commit()

        d = key.to_dict()
        assert d['scopes'] == []

        db_session.delete(key)
        db_session.commit()

    def test_to_dict_includes_rate_limit(self, app, db_session):
        """to_dict should include rate_limit field."""
        from models.security import ApiKey

        raw_key = secrets.token_hex(32)
        key = ApiKey(
            name='Test',
            key_hash=hashlib.sha256(raw_key.encode()).hexdigest(),
            key_prefix=raw_key[:8],
            scopes='read:diary',
            rate_limit=60,
            is_active=True,
        )
        db_session.add(key)
        db_session.commit()

        d = key.to_dict()
        assert d['rate_limit'] == 60

        db_session.delete(key)
        db_session.commit()

    def test_to_dict_optional_dates(self, app, db_session):
        """last_used and expires_at should only appear when set."""
        from models.security import ApiKey

        raw_key = secrets.token_hex(32)
        key = ApiKey(
            name='Test',
            key_hash=hashlib.sha256(raw_key.encode()).hexdigest(),
            key_prefix=raw_key[:8],
            scopes='read:diary',
            is_active=True,
        )
        db_session.add(key)
        db_session.commit()

        d = key.to_dict()
        assert 'last_used' not in d
        assert 'expires_at' not in d

        # Set dates
        key.last_used = datetime.utcnow()
        key.expires_at = datetime.utcnow() + timedelta(days=30)
        db_session.commit()

        d = key.to_dict()
        assert 'last_used' in d
        assert 'expires_at' in d

        db_session.delete(key)
        db_session.commit()


class TestApiAccessLogModel:
    """Tests for the ApiAccessLog model."""

    def test_to_dict_serialization(self, app, db_session):
        """to_dict should serialize all fields correctly."""
        from models.security import ApiKey, ApiAccessLog

        raw_key = secrets.token_hex(32)
        key = ApiKey(
            name='Test',
            key_hash=hashlib.sha256(raw_key.encode()).hexdigest(),
            key_prefix=raw_key[:8],
            scopes='read:diary',
            is_active=True,
        )
        db_session.add(key)
        db_session.commit()

        log = ApiAccessLog(
            key_id=key.id,
            endpoint='/api/v1/diary/entries',
            method='GET',
            status_code=200,
            ip_address='127.0.0.1',
        )
        db_session.add(log)
        db_session.commit()

        d = log.to_dict()
        assert d['endpoint'] == '/api/v1/diary/entries'
        assert d['method'] == 'GET'
        assert d['status_code'] == 200
        assert d['ip_address'] == '127.0.0.1'
        assert d['key_prefix'] == raw_key[:8] + '****'
        assert 'timestamp' in d

        db_session.delete(log)
        db_session.delete(key)
        db_session.commit()

    def test_to_dict_null_key(self, app, db_session):
        """Log entry without key_id should have null key_prefix."""
        from models.security import ApiAccessLog

        log = ApiAccessLog(
            key_id=None,
            endpoint='/api/v1/fodmap/categories',
            method='GET',
            status_code=401,
            ip_address='10.0.0.1',
        )
        db_session.add(log)
        db_session.commit()

        d = log.to_dict()
        assert d['key_prefix'] is None
        assert d['key_id'] is None

        db_session.delete(log)
        db_session.commit()
