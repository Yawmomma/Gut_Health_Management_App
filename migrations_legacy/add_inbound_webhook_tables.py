"""
Migration: Add inbound webhook tables (external_webhook_logs, billing_events)
Date: 2026-02-28

Creates tables for receiving inbound webhooks from external services
(wearables, meal trackers) and billing providers (Stripe, App Store).

Note: Tables are also auto-created by db.create_all() on app startup.
This script exists as a safety net for existing deployments.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app
from database import db


def migrate():
    """Create external_webhook_logs and billing_events tables"""
    with app.app_context():
        try:
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS external_webhook_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source VARCHAR(50) NOT NULL,
                    provider VARCHAR(100),
                    event_type VARCHAR(100) NOT NULL,
                    payload TEXT NOT NULL,
                    signature_header VARCHAR(500),
                    signature_valid BOOLEAN,
                    processed BOOLEAN DEFAULT 0,
                    processing_notes TEXT,
                    http_status_returned INTEGER DEFAULT 200,
                    received_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))

            db.session.execute(db.text("""
                CREATE INDEX IF NOT EXISTS ix_external_webhook_logs_received_at
                ON external_webhook_logs (received_at)
            """))

            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS billing_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider VARCHAR(50) NOT NULL,
                    event_type VARCHAR(100) NOT NULL,
                    event_id VARCHAR(200) UNIQUE,
                    payload TEXT NOT NULL,
                    signature_header VARCHAR(500),
                    signature_valid BOOLEAN,
                    processed BOOLEAN DEFAULT 0,
                    processing_notes TEXT,
                    received_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))

            db.session.execute(db.text("""
                CREATE INDEX IF NOT EXISTS ix_billing_events_received_at
                ON billing_events (received_at)
            """))

            db.session.commit()
            print("Successfully created inbound webhook tables:")
            print("  - external_webhook_logs (with received_at index)")
            print("  - billing_events (with received_at index, unique event_id)")

        except Exception as e:
            db.session.rollback()
            print(f"Error during migration: {str(e)}")
            raise


if __name__ == '__main__':
    migrate()
