"""
Migration to add custom nutrients and vitamin unit columns to the foods table.

Run this script to add:
- custom_nutrients (TEXT) - JSON string for custom vitamins, minerals, macros
- vitamin_a_unit, vitamin_b12_unit, vitamin_d_unit, riboflavin_b2_unit (VARCHAR(20))
"""

import sqlite3
import os

def migrate():
    """Add custom_nutrients and vitamin unit columns to foods table"""
    # Get the database path
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance', 'gut_health.db')

    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(foods)")
        columns = [col[1] for col in cursor.fetchall()]

        columns_to_add = [
            ('custom_nutrients', 'TEXT'),
            ('vitamin_a_unit', 'VARCHAR(20) DEFAULT "mcg"'),
            ('vitamin_b12_unit', 'VARCHAR(20) DEFAULT "mcg"'),
            ('vitamin_d_unit', 'VARCHAR(20) DEFAULT "mcg"'),
            ('riboflavin_b2_unit', 'VARCHAR(20) DEFAULT "mg"'),
        ]

        for col_name, col_type in columns_to_add:
            if col_name not in columns:
                cursor.execute(f'ALTER TABLE foods ADD COLUMN {col_name} {col_type}')
                print(f"Added column: {col_name}")
            else:
                print(f"Column already exists: {col_name}")

        conn.commit()
        print("Migration completed successfully!")
        return True

    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {str(e)}")
        return False

    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
