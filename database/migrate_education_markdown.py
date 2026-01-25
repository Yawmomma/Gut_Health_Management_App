"""
Database migration to add markdown support to educational_content table

Run this once to add the new columns:
python database/migrate_education_markdown.py
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from database import db

def migrate():
    """Add markdown columns to educational_content table"""
    with app.app_context():
        try:
            # Check if columns already exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('educational_content')]

            # Add missing columns
            if 'markdown_source' not in columns:
                print("Adding 'markdown_source' column...")
                db.session.execute(db.text(
                    "ALTER TABLE educational_content ADD COLUMN markdown_source TEXT"
                ))

            if 'filename' not in columns:
                print("Adding 'filename' column...")
                db.session.execute(db.text(
                    "ALTER TABLE educational_content ADD COLUMN filename VARCHAR(500)"
                ))

            if 'is_markdown' not in columns:
                print("Adding 'is_markdown' column...")
                db.session.execute(db.text(
                    "ALTER TABLE educational_content ADD COLUMN is_markdown BOOLEAN DEFAULT 0"
                ))

            db.session.commit()
            print("\n[SUCCESS] Migration completed successfully!")
            print("Your database now supports markdown chapters.")

        except Exception as e:
            db.session.rollback()
            print(f"\n[ERROR] Migration failed: {e}")
            print("If columns already exist, this is normal - no changes needed.")

if __name__ == '__main__':
    print("Educational Content Markdown Migration")
    print("=" * 50)
    migrate()
