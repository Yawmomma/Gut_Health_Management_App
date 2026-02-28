"""
Migration: Add custom_nutrients field to foods table
Date: 2026-02-03
Description: Adds a TEXT field to store custom nutritional data as JSON when USDA link is unavailable
"""

import sqlite3
import os

def run_migration():
    """Add custom_nutrients column to foods table"""
    db_path = os.path.join('instance', 'gut_health.db')

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(foods)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'custom_nutrients' in columns:
            print("Column 'custom_nutrients' already exists in foods table")
            return

        # Add the custom_nutrients column (TEXT to store JSON)
        cursor.execute("""
            ALTER TABLE foods
            ADD COLUMN custom_nutrients TEXT
        """)

        conn.commit()
        print("[OK] Successfully added custom_nutrients column to foods table")
        print("     Column stores custom nutritional data as JSON")

    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    print("Running migration: Add custom_nutrients field to foods table")
    run_migration()
    print("Migration complete!")
