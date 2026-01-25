"""
Migration script to add serving type and note fields
Adds serving_type and serving_note fields for safe, moderate, and high servings
"""
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import app
from database import db

def upgrade():
    """Add new columns for serving types and notes"""
    with app.app_context():
        print("Adding serving type and note columns...")

        # SQL to add new columns
        alter_statements = [
            # Safe serving type and note
            "ALTER TABLE foods ADD COLUMN safe_serving_type VARCHAR(50)",
            "ALTER TABLE foods ADD COLUMN safe_serving_note VARCHAR(200)",

            # Moderate serving type and note
            "ALTER TABLE foods ADD COLUMN moderate_serving_type VARCHAR(50)",
            "ALTER TABLE foods ADD COLUMN moderate_serving_note VARCHAR(200)",

            # High serving type and note
            "ALTER TABLE foods ADD COLUMN high_serving_type VARCHAR(50)",
            "ALTER TABLE foods ADD COLUMN high_serving_note VARCHAR(200)",
        ]

        for statement in alter_statements:
            try:
                db.session.execute(db.text(statement))
                print(f"✓ Executed: {statement}")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print(f"⊘ Column already exists, skipping: {statement}")
                else:
                    print(f"✗ Error: {e}")
                    raise

        db.session.commit()
        print("\n✓ Migration completed successfully!")
        print("\nServing type and note fields have been added for safe, moderate, and high servings.")

if __name__ == '__main__':
    print("=" * 60)
    print("SERVING TYPE AND NOTE MIGRATION")
    print("=" * 60)
    upgrade()
