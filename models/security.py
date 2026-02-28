"""
Security Models
For API keys, rate limiting, access control, and audit logging
"""

from database import db
from datetime import datetime


class ApiKey(db.Model):
    """Represents an API key for external access"""
    __tablename__ = 'api_keys'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "App2 access"
    key_hash = db.Column(db.String(64), unique=True, nullable=False)  # SHA-256 hash of key
    key_prefix = db.Column(db.String(8), nullable=False)  # First 8 chars for identification
    is_active = db.Column(db.Boolean, default=True)
    scopes = db.Column(db.String(500))  # CSV: 'read:diary,read:analytics,read:foods'
    rate_limit = db.Column(db.Integer, default=120)  # Requests per minute (60=LOW, 120=MEDIUM/HIGH)
    last_used = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)

    # Relationship to access logs
    access_logs = db.relationship('ApiAccessLog', backref='api_key', lazy='dynamic')

    def to_dict(self, include_none_fields=False):
        """Serialize API key to dictionary (never includes actual key)"""
        data = {
            'id': self.id,
            'name': self.name,
            'key_prefix': self.key_prefix + '****',  # Show first 8 chars + mask
            'is_active': self.is_active,
            'scopes': self.scopes.split(',') if self.scopes else [],
            'rate_limit': self.rate_limit or 120,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if self.last_used:
            data['last_used'] = self.last_used.isoformat()
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        return data


class ApiAccessLog(db.Model):
    """Audit log for all authenticated API requests"""
    __tablename__ = 'api_access_logs'

    id = db.Column(db.Integer, primary_key=True)
    key_id = db.Column(db.Integer, db.ForeignKey('api_keys.id'), nullable=True)
    endpoint = db.Column(db.String(500), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    status_code = db.Column(db.Integer, nullable=False)
    ip_address = db.Column(db.String(45))  # IPv6 max length
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        """Serialize access log entry to dictionary"""
        return {
            'id': self.id,
            'key_id': self.key_id,
            'key_prefix': self.api_key.key_prefix + '****' if self.api_key else None,
            'endpoint': self.endpoint,
            'method': self.method,
            'status_code': self.status_code,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }
