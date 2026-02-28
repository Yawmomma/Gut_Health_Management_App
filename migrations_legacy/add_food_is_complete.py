"""
Migration: Add is_complete field to foods table
Date: 2026-01-30
Description: Adds a boolean field to track whether a food entry is complete or needs more information
"""

import sqlite3
import os

def run_migration():
    """Add is_complete column to foods table"""
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

        if 'is_complete' in columns:
            print("Column 'is_complete' already exists in foods table")
            return

        # Add the is_complete column with default value True (existing foods are assumed complete)
        cursor.execute("""
            ALTER TABLE foods
            ADD COLUMN is_complete BOOLEAN DEFAULT 1
        """)

        conn.commit()
        print("[OK] Successfully added is_complete column to foods table")
        print("     All existing foods marked as complete (is_complete=True)")

    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    print("Running migration: Add is_complete field to foods table")
    run_migration()
    print("Migration complete!")
