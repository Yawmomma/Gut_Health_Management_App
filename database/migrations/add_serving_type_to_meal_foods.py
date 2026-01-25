"""
Migration script to add serving_type field to meal_foods table
This allows tracking which serving size (safe, moderate, high) was logged for each food
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
    """Add serving_type column to meal_foods table"""
    with app.app_context():
        print("Adding serving_type column to meal_foods table...")

        # SQL to add new column
        alter_statement = "ALTER TABLE meal_foods ADD COLUMN serving_type VARCHAR(20)"

        try:
            db.session.execute(db.text(alter_statement))
            print(f"✓ Executed: {alter_statement}")
            db.session.commit()
            print("\n✓ Migration completed successfully!")
            print("\nThe serving_type field has been added to meal_foods table.")
            print("This allows tracking whether foods were logged as safe, moderate, or high servings.")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print(f"⊘ Column already exists, skipping: {alter_statement}")
            else:
                print(f"✗ Error: {e}")
                raise

if __name__ == '__main__':
    print("=" * 60)
    print("ADD SERVING_TYPE TO MEAL_FOODS MIGRATION")
    print("=" * 60)
    upgrade()
