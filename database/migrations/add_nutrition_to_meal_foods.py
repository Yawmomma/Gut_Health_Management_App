"""
Migration to add nutrition fields to meal_foods table
Run this script to add the new columns for storing calculated nutrition values.
"""

import sqlite3
import os

def migrate():
    """Add nutrition columns to meal_foods table"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance', 'gut_health.db')

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check existing columns
    cursor.execute("PRAGMA table_info(meal_foods)")
    existing_columns = [col[1] for col in cursor.fetchall()]

    columns_to_add = [
        ('num_servings', 'FLOAT'),
        ('energy_kj', 'FLOAT'),
        ('protein_g', 'FLOAT'),
        ('fat_g', 'FLOAT'),
        ('carbs_g', 'FLOAT'),
        ('sodium_mg', 'FLOAT'),
    ]

    for col_name, col_type in columns_to_add:
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE meal_foods ADD COLUMN {col_name} {col_type}")
                print(f"Added column: {col_name}")
            except sqlite3.OperationalError as e:
                print(f"Column {col_name} may already exist: {e}")
        else:
            print(f"Column {col_name} already exists")

    conn.commit()
    conn.close()
    print("Migration completed successfully!")
    return True

if __name__ == '__main__':
    migrate()
