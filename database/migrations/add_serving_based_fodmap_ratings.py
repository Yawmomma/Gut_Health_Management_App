"""
Migration script to add serving-based FODMAP ratings
Adds separate FODMAP ratings for safe, moderate, and high servings
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
    """Add new columns for serving-based FODMAP ratings"""
    with app.app_context():
        print("Adding serving-based FODMAP rating columns...")

        # SQL to add new columns
        alter_statements = [
            # Safe serving FODMAP ratings
            "ALTER TABLE foods ADD COLUMN safe_fructans VARCHAR(20)",
            "ALTER TABLE foods ADD COLUMN safe_gos VARCHAR(20)",
            "ALTER TABLE foods ADD COLUMN safe_lactose VARCHAR(20)",
            "ALTER TABLE foods ADD COLUMN safe_fructose VARCHAR(20)",
            "ALTER TABLE foods ADD COLUMN safe_polyols VARCHAR(20)",
            "ALTER TABLE foods ADD COLUMN safe_mannitol VARCHAR(20)",
            "ALTER TABLE foods ADD COLUMN safe_sorbitol VARCHAR(20)",

            # Moderate serving FODMAP ratings
            "ALTER TABLE foods ADD COLUMN moderate_fructans VARCHAR(20)",
            "ALTER TABLE foods ADD COLUMN moderate_gos VARCHAR(20)",
            "ALTER TABLE foods ADD COLUMN moderate_lactose VARCHAR(20)",
            "ALTER TABLE foods ADD COLUMN moderate_fructose VARCHAR(20)",
            "ALTER TABLE foods ADD COLUMN moderate_polyols VARCHAR(20)",
            "ALTER TABLE foods ADD COLUMN moderate_mannitol VARCHAR(20)",
            "ALTER TABLE foods ADD COLUMN moderate_sorbitol VARCHAR(20)",

            # High serving FODMAP ratings
            "ALTER TABLE foods ADD COLUMN high_fructans VARCHAR(20)",
            "ALTER TABLE foods ADD COLUMN high_gos VARCHAR(20)",
            "ALTER TABLE foods ADD COLUMN high_lactose VARCHAR(20)",
            "ALTER TABLE foods ADD COLUMN high_fructose VARCHAR(20)",
            "ALTER TABLE foods ADD COLUMN high_polyols VARCHAR(20)",
            "ALTER TABLE foods ADD COLUMN high_mannitol VARCHAR(20)",
            "ALTER TABLE foods ADD COLUMN high_sorbitol VARCHAR(20)",
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
        print("\nNote: Old single FODMAP rating columns (fructans, gos, etc.) are kept for backward compatibility.")
        print("They can be removed in a future migration after data is migrated.")

if __name__ == '__main__':
    print("=" * 60)
    print("SERVING-BASED FODMAP RATINGS MIGRATION")
    print("=" * 60)
    upgrade()
