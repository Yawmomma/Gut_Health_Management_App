"""
Migration: Add recipe_id column to meals table
Run this to update the database schema
"""

from database import db
from app import app

def migrate():
    """Add recipe_id column to meals table"""
    with app.app_context():
        try:
            # Check if column already exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('meals')]

            if 'recipe_id' not in columns:
                # Add the column using raw SQL
                db.engine.execute('ALTER TABLE meals ADD COLUMN recipe_id INTEGER')
                print("✓ Added recipe_id column to meals table")
            else:
                print("✓ recipe_id column already exists")

        except Exception as e:
            print(f"Error during migration: {e}")
            raise

if __name__ == '__main__':
    migrate()
