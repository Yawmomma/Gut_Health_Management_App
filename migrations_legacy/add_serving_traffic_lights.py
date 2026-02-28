"""
Migration: Add traffic light color fields for each serving type
Date: 2026-02-10
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app
from database import db

def migrate():
    """Add safe_traffic_light, moderate_traffic_light, and high_traffic_light columns to foods table"""
    with app.app_context():
        try:
            # Add new columns with default values
            db.session.execute(db.text("""
                ALTER TABLE foods
                ADD COLUMN safe_traffic_light VARCHAR(20) DEFAULT 'Green'
            """))

            db.session.execute(db.text("""
                ALTER TABLE foods
                ADD COLUMN moderate_traffic_light VARCHAR(20) DEFAULT 'Amber'
            """))

            db.session.execute(db.text("""
                ALTER TABLE foods
                ADD COLUMN high_traffic_light VARCHAR(20) DEFAULT 'Red'
            """))

            db.session.commit()
            print("✓ Successfully added traffic light columns to foods table")
            print("  - safe_traffic_light (default: Green)")
            print("  - moderate_traffic_light (default: Amber)")
            print("  - high_traffic_light (default: Red)")

        except Exception as e:
            db.session.rollback()
            print(f"✗ Error during migration: {str(e)}")
            raise

if __name__ == '__main__':
    migrate()
