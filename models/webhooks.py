"""
Webhook models for real-time event notifications
"""

from database import db
from datetime import datetime


class Webhook(db.Model):
    """
    Webhook registration for event notifications
    Stores webhook URLs that should receive notifications when specific events occur
    """
    __tablename__ = 'webhooks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # User-friendly name
    url = db.Column(db.String(500), nullable=False)  # Webhook endpoint URL
    events = db.Column(db.Text, nullable=False)  # Comma-separated list of event types
    is_active = db.Column(db.Boolean, default=True)  # Enable/disable webhook
    secret = db.Column(db.String(100))  # Optional secret for HMAC validation

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_triggered = db.Column(db.DateTime)  # Last time webhook was triggered
    trigger_count = db.Column(db.Integer, default=0)  # Total number of triggers
    last_error = db.Column(db.Text)  # Last error message if trigger failed

    def __repr__(self):
        return f'<Webhook {self.name}>'

    def to_dict(self):
        """Convert webhook to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'events': [e.strip() for e in self.events.split(',') if e.strip()],
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None,
            'trigger_count': self.trigger_count,
            'last_error': self.last_error
        }

    @property
    def event_list(self):
        """Get list of events this webhook subscribes to"""
        return [e.strip() for e in self.events.split(',') if e.strip()]


class EventLog(db.Model):
    """
    Log of events that occurred in the system
    Used for SSE stream and webhook triggers
    """
    __tablename__ = 'event_logs'

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)  # entry_created, entry_updated, etc.
    entity_type = db.Column(db.String(50))  # meal, symptom, bowel, etc.
    entity_id = db.Column(db.Integer)  # ID of the affected entity
    user_id = db.Column(db.Integer)  # For multi-user support (future)
    data = db.Column(db.Text)  # JSON data about the event
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<EventLog {self.event_type}>'

    def to_dict(self):
        """Convert event log to dictionary"""
        import json
        return {
            'id': self.id,
            'event_type': self.event_type,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'data': json.loads(self.data) if self.data else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ExternalWebhookLog(db.Model):
    """
    Log of inbound webhooks received from external services
    (wearables, meal trackers, health apps)
    """
    __tablename__ = 'external_webhook_logs'

    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(50), nullable=False)       # wearable_sync, meal_tracker, health_app
    provider = db.Column(db.String(100))                      # fitbit, oura, apple_watch, myfitnesspal, etc.
    event_type = db.Column(db.String(100), nullable=False)   # heart_rate, sleep, stress, meal_import, etc.
    payload = db.Column(db.Text, nullable=False)              # Raw JSON payload
    signature_header = db.Column(db.String(500))              # Raw signature header received
    signature_valid = db.Column(db.Boolean)                   # True/False/None (no sig check configured)
    processed = db.Column(db.Boolean, default=False)          # Whether data has been converted to diary entries
    processing_notes = db.Column(db.Text)                     # Notes or error messages from processing
    http_status_returned = db.Column(db.Integer, default=200)
    received_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<ExternalWebhookLog {self.source}/{self.provider}/{self.event_type}>'

    def to_dict(self):
        """Convert to dictionary"""
        import json
        return {
            'id': self.id,
            'source': self.source,
            'provider': self.provider,
            'event_type': self.event_type,
            'payload': json.loads(self.payload) if self.payload else None,
            'signature_valid': self.signature_valid,
            'processed': self.processed,
            'processing_notes': self.processing_notes,
            'received_at': self.received_at.isoformat() if self.received_at else None
        }


class BillingEvent(db.Model):
    """
    Log of billing/subscription webhook events from Stripe or App Store
    """
    __tablename__ = 'billing_events'

    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(50), nullable=False)       # stripe, app_store, google_play
    event_type = db.Column(db.String(100), nullable=False)    # subscription.created, payment.failed, etc.
    event_id = db.Column(db.String(200), unique=True)         # External event ID for idempotency
    payload = db.Column(db.Text, nullable=False)               # Raw JSON payload
    signature_header = db.Column(db.String(500))               # Raw signature header
    signature_valid = db.Column(db.Boolean)                    # Signature validation result
    processed = db.Column(db.Boolean, default=False)           # Whether subscription status was updated
    processing_notes = db.Column(db.Text)                      # Notes/errors from processing
    received_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<BillingEvent {self.provider}/{self.event_type}>'

    def to_dict(self):
        """Convert to dictionary"""
        import json
        return {
            'id': self.id,
            'provider': self.provider,
            'event_type': self.event_type,
            'event_id': self.event_id,
            'payload': json.loads(self.payload) if self.payload else None,
            'signature_valid': self.signature_valid,
            'processed': self.processed,
            'processing_notes': self.processing_notes,
            'received_at': self.received_at.isoformat() if self.received_at else None
        }
