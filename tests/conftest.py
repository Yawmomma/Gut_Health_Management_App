"""
Shared test fixtures for the Gut Health Management App test suite.
Provides app, client, database, and API key fixtures.
"""

import os
import sys
import pytest
import secrets
import hashlib
import tempfile

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope='session')
def app():
    """Create application configured for testing with a temporary database."""
    # Create a temp file for the test database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')

    # Must set config before importing app to avoid side effects
    os.environ['SECRET_KEY'] = 'test-secret-key'

    from app import app as flask_app
    from database import db

    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
    })

    with flask_app.app_context():
        db.create_all()

    yield flask_app

    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope='function')
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Provide a clean database session for each test."""
    from database import db

    with app.app_context():
        yield db.session
        db.session.rollback()


def _create_api_key(db_session, name='Test Key', scopes='read:fodmap', rate_limit=120,
                    is_active=True, expires_at=None):
    """Helper to create an API key and return (raw_key, ApiKey object)."""
    from models.security import ApiKey

    raw_key = secrets.token_hex(32)
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    api_key = ApiKey(
        name=name,
        key_hash=key_hash,
        key_prefix=raw_key[:8],
        scopes=scopes,
        rate_limit=rate_limit,
        is_active=is_active,
        expires_at=expires_at,
    )
    db_session.add(api_key)
    db_session.commit()

    return raw_key, api_key


@pytest.fixture(scope='function')
def api_key(app, db_session):
    """Create a test API key with basic read scopes."""
    raw_key, key_obj = _create_api_key(
        db_session,
        name='Test Key',
        scopes='read:fodmap,read:diary,read:analytics,read:recipes'
    )
    yield raw_key, key_obj

    # Cleanup
    from models.security import ApiAccessLog
    ApiAccessLog.query.filter_by(key_id=key_obj.id).delete()
    db_session.delete(key_obj)
    db_session.commit()


@pytest.fixture(scope='function')
def admin_key(app, db_session):
    """Create a test API key with admin scopes."""
    raw_key, key_obj = _create_api_key(
        db_session,
        name='Admin Test Key',
        scopes='admin:security,admin:backup,admin:settings,admin:users,'
               'read:fodmap,read:diary,read:analytics,read:recipes,'
               'write:diary,write:recipes,read:security'
    )
    yield raw_key, key_obj

    # Cleanup
    from models.security import ApiAccessLog
    ApiAccessLog.query.filter_by(key_id=key_obj.id).delete()
    db_session.delete(key_obj)
    db_session.commit()
