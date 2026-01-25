"""
Migration script to add serving-based histamine ratings
Adds separate histamine ratings for safe, moderate, and high servings
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
    """Add new columns for serving-based histamine ratings"""
    with app.app_context():
        print("Adding serving-based histamine rating columns...")

        # SQL to add new columns
        alter_statements = [
            # Safe serving histamine ratings
            "ALTER TABLE foods ADD COLUMN safe_histamine_level VARCHAR(50)",
            "ALTER TABLE foods ADD COLUMN safe_histamine_liberator VARCHAR(10)",
            "ALTER TABLE foods ADD COLUMN safe_dao_blocker VARCHAR(10)",

            # Moderate serving histamine ratings
            "ALTER TABLE foods ADD COLUMN moderate_histamine_level VARCHAR(50)",
            "ALTER TABLE foods ADD COLUMN moderate_histamine_liberator VARCHAR(10)",
            "ALTER TABLE foods ADD COLUMN moderate_dao_blocker VARCHAR(10)",

            # High serving histamine ratings
            "ALTER TABLE foods ADD COLUMN high_histamine_level VARCHAR(50)",
            "ALTER TABLE foods ADD COLUMN high_histamine_liberator VARCHAR(10)",
            "ALTER TABLE foods ADD COLUMN high_dao_blocker VARCHAR(10)",
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
        print("\nNote: Old single histamine rating columns are kept for backward compatibility.")

if __name__ == '__main__':
    print("=" * 60)
    print("SERVING-BASED HISTAMINE RATINGS MIGRATION")
    print("=" * 60)
    upgrade()
