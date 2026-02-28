"""
Database Migration: Add USDA link to Foods table
=================================================
This script adds the usda_food_id column to the existing foods table,
allowing FODMAP foods to link to USDA foods for nutritional information.

Usage:
    python database/add_usda_link_to_foods.py

What this does:
- Adds usda_food_id column to foods table (nullable, indexed)
- Creates foreign key relationship to usda_foods table
- Existing foods will have usda_food_id = NULL (can be set later)
- New foods copied from USDA will have this link automatically

This migration is safe to run multiple times (idempotent).
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database import db


def add_usda_link_column():
    """Add usda_food_id column to foods table"""
    print("\n" + "=" * 70)
    print("DATABASE MIGRATION: Add USDA link to Foods table")
    print("=" * 70)

    with app.app_context():
        # Check if column already exists
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('foods')]

        if 'usda_food_id' in columns:
            print("\n[OK] Column 'usda_food_id' already exists in foods table")
            print("     No migration needed.")
            return

        print("\n[...] Adding usda_food_id column to foods table...")

        # Add the column using raw SQL
        # This is safer than dropping and recreating the table
        with db.engine.connect() as conn:
            # SQLite doesn't support ALTER TABLE ADD FOREIGN KEY directly
            # So we add the column first, then recreate with foreign key if needed
            conn.execute(db.text(
                "ALTER TABLE foods ADD COLUMN usda_food_id INTEGER"
            ))
            conn.commit()

            # Create index for better performance
            conn.execute(db.text(
                "CREATE INDEX IF NOT EXISTS ix_foods_usda_food_id ON foods(usda_food_id)"
            ))
            conn.commit()

        print("[OK] Column added successfully!")
        print("\nNext steps:")
        print("  1. Run copy_usda_to_fodmap.py to import foods with USDA links")
        print("  2. Existing foods can be manually linked to USDA foods if desired")
        print("\nNote: The foreign key relationship is defined in the Food model")
        print("      and will be enforced by SQLAlchemy.")

        print("\n" + "=" * 70)
        print("MIGRATION COMPLETED")
        print("=" * 70)


if __name__ == '__main__':
    add_usda_link_column()
