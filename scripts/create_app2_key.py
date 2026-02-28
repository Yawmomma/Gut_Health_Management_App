"""
APP2 Bootstrap Key Generator
Creates an API key with the scopes APP2 needs to consume the API.

Usage:
    python scripts/create_app2_key.py [--secondary]

Options:
    --secondary    Include secondary feature scopes (gamification, reintroduction, etc.)

The generated key is printed ONCE and cannot be retrieved again.
Store it securely in APP2's environment/config.
"""

import sys
import os
import secrets
import hashlib
from datetime import datetime

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from database import db
from models.security import ApiKey


# Primary scopes — APP2 needs these from day one
PRIMARY_SCOPES = [
    'read:diary',
    'read:analytics',
    'read:export',
    'read:chat',
    'read:compendium',
    'read:fodmap',
    'read:usda',
    'read:ausnut',
    'read:foods',
    'read:recipes',
    'read:search',
    'read:webhooks',
    'write:diary',
    'write:webhooks',
    'stream:realtime',
]

# Secondary scopes — add later when APP2 builds these features
SECONDARY_SCOPES = [
    'read:gamification',
    'read:reintroduction',
    'read:notifications',
    'read:billing',
    'read:education',
    'read:help',
]

# APP2 should NEVER have these scopes
# admin:security, admin:backup, admin:settings, admin:users
# write:foods, write:recipes, write:education, write:help


def create_app2_key(include_secondary=False):
    """Generate the APP2 bootstrap API key."""

    scopes = PRIMARY_SCOPES.copy()
    if include_secondary:
        scopes.extend(SECONDARY_SCOPES)

    scope_str = ','.join(scopes)

    # Generate cryptographically secure key
    raw_key = secrets.token_hex(32)  # 64 hex characters
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    key_prefix = raw_key[:8]

    key_name = 'APP2 Primary + Secondary' if include_secondary else 'APP2 Primary'

    api_key = ApiKey(
        name=key_name,
        key_hash=key_hash,
        key_prefix=key_prefix,
        scopes=scope_str,
        rate_limit=120,  # MEDIUM/HIGH tier
        is_active=True,
        expires_at=None  # No expiry — revoke manually if needed
    )
    db.session.add(api_key)
    db.session.commit()

    return raw_key, api_key


def main():
    include_secondary = '--secondary' in sys.argv

    with app.app_context():
        # Check if an APP2 key already exists
        existing = ApiKey.query.filter(
            ApiKey.name.like('APP2%'),
            ApiKey.is_active == True
        ).first()

        if existing:
            print(f'\nWARNING: An active APP2 key already exists:')
            print(f'  Name: {existing.name}')
            print(f'  Prefix: {existing.key_prefix}****')
            print(f'  Created: {existing.created_at}')
            print(f'\nTo create a new key, first revoke the existing one via:')
            print(f'  DELETE /api/v1/auth/api-keys/{existing.id}')
            print(f'\nOr pass --force to create another key anyway.')

            if '--force' not in sys.argv:
                sys.exit(1)

        raw_key, api_key = create_app2_key(include_secondary)

        scope_type = 'Primary + Secondary' if include_secondary else 'Primary only'

        print('\n' + '=' * 60)
        print('  APP2 API KEY CREATED SUCCESSFULLY')
        print('=' * 60)
        print(f'\n  Name:       {api_key.name}')
        print(f'  Key ID:     {api_key.id}')
        print(f'  Prefix:     {api_key.key_prefix}****')
        print(f'  Rate Limit: {api_key.rate_limit}/min')
        print(f'  Scopes:     {scope_type} ({len(api_key.scopes.split(","))} scopes)')
        print(f'  Created:    {api_key.created_at}')
        print(f'\n  API KEY (store this securely — shown ONCE only):')
        print(f'\n  {raw_key}')
        print(f'\n  Usage in APP2:')
        print(f'    X-API-Key: {raw_key}')
        print(f'    or')
        print(f'    Authorization: Bearer {raw_key}')
        print('\n' + '=' * 60)
        print('\n  IMPORTANT: This key cannot be retrieved again.')
        print('  Store it in APP2\'s .env or config file immediately.')
        print()


if __name__ == '__main__':
    main()
