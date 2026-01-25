"""
Migration script to add image_path column to recipes and saved_meals tables
Run this script once to update existing database
"""

import sqlite3
import os

# Get the database path
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance', 'gut_health.db')

def migrate():
    """Add image_path column to recipes and saved_meals tables"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if image_path column exists in recipes table
        cursor.execute("PRAGMA table_info(recipes)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'image_path' not in columns:
            print("Adding image_path column to recipes table...")
            cursor.execute("ALTER TABLE recipes ADD COLUMN image_path VARCHAR(500)")
            print("[OK] Successfully added image_path to recipes table")
        else:
            print("[SKIP] image_path column already exists in recipes table")

        # Check if image_path column exists in saved_meals table
        cursor.execute("PRAGMA table_info(saved_meals)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'image_path' not in columns:
            print("Adding image_path column to saved_meals table...")
            cursor.execute("ALTER TABLE saved_meals ADD COLUMN image_path VARCHAR(500)")
            print("[OK] Successfully added image_path to saved_meals table")
        else:
            print("[SKIP] image_path column already exists in saved_meals table")

        conn.commit()
        print("\n[OK] Migration completed successfully!")

    except Exception as e:
        print(f"\n[ERROR] Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("DATABASE MIGRATION: Add image_path to recipes and meals")
    print("=" * 60)
    migrate()
