"""
Migration script to add nutrition information columns to foods table
Run this script once to update existing database
"""

import sqlite3
import os

# Get the database path
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance', 'gut_health.db')

def migrate():
    """Add nutrition information columns to foods table"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # List of all columns to add
    nutrition_columns = [
        ("health_star_rating", "REAL"),
        ("serving_size", "VARCHAR(50)"),
        ("servings_per_pack", "INTEGER"),
        # Energy
        ("energy_per_serve_kj", "REAL"),
        ("energy_per_100_kj", "REAL"),
        ("energy_per_serve_cal", "REAL"),
        ("energy_per_100_cal", "REAL"),
        # Macronutrients per serve
        ("protein_per_serve", "REAL"),
        ("fat_per_serve", "REAL"),
        ("saturated_fat_per_serve", "REAL"),
        ("trans_fat_per_serve", "REAL"),
        ("polyunsaturated_fat_per_serve", "REAL"),
        ("monounsaturated_fat_per_serve", "REAL"),
        ("carbohydrate_per_serve", "REAL"),
        ("sugars_per_serve", "REAL"),
        ("lactose_per_serve", "REAL"),
        ("galactose_per_serve", "REAL"),
        ("dietary_fibre_per_serve", "REAL"),
        # Macronutrients per 100ml/100g
        ("protein_per_100", "REAL"),
        ("fat_per_100", "REAL"),
        ("saturated_fat_per_100", "REAL"),
        ("trans_fat_per_100", "REAL"),
        ("polyunsaturated_fat_per_100", "REAL"),
        ("monounsaturated_fat_per_100", "REAL"),
        ("carbohydrate_per_100", "REAL"),
        ("sugars_per_100", "REAL"),
        ("lactose_per_100", "REAL"),
        ("galactose_per_100", "REAL"),
        ("dietary_fibre_per_100", "REAL"),
        # Cholesterol
        ("cholesterol_per_serve", "REAL"),
        ("cholesterol_per_100", "REAL"),
        # Minerals per serve
        ("sodium_per_serve", "REAL"),
        ("potassium_per_serve", "REAL"),
        ("calcium_per_serve", "REAL"),
        ("phosphorus_per_serve", "REAL"),
        # Minerals per 100ml/100g
        ("sodium_per_100", "REAL"),
        ("potassium_per_100", "REAL"),
        ("calcium_per_100", "REAL"),
        ("phosphorus_per_100", "REAL"),
        # Vitamins per serve
        ("vitamin_a_per_serve", "REAL"),
        ("vitamin_b12_per_serve", "REAL"),
        ("vitamin_d_per_serve", "REAL"),
        ("riboflavin_b2_per_serve", "REAL"),
        # Vitamins per 100ml/100g
        ("vitamin_a_per_100", "REAL"),
        ("vitamin_b12_per_100", "REAL"),
        ("vitamin_d_per_100", "REAL"),
        ("riboflavin_b2_per_100", "REAL"),
        # RDI percentages
        ("vitamin_a_rdi_percent", "VARCHAR(20)"),
        ("vitamin_b12_rdi_percent", "VARCHAR(20)"),
        ("vitamin_d_rdi_percent", "VARCHAR(20)"),
        ("riboflavin_b2_rdi_percent", "VARCHAR(20)"),
        ("calcium_rdi_percent", "VARCHAR(20)"),
        ("phosphorus_rdi_percent", "VARCHAR(20)"),
        # Ingredients and where to buy
        ("ingredients_list", "TEXT"),
        ("contains_allergens", "VARCHAR(200)"),
        ("may_contain_allergens", "VARCHAR(200)"),
        ("where_to_buy", "TEXT"),
    ]

    try:
        # Get existing columns
        cursor.execute("PRAGMA table_info(foods)")
        existing_columns = [column[1] for column in cursor.fetchall()]

        added_count = 0
        skipped_count = 0

        for column_name, column_type in nutrition_columns:
            if column_name not in existing_columns:
                print(f"Adding {column_name} column to foods table...")
                cursor.execute(f"ALTER TABLE foods ADD COLUMN {column_name} {column_type}")
                added_count += 1
            else:
                skipped_count += 1

        conn.commit()
        print("\n" + "=" * 60)
        print(f"[OK] Migration completed successfully!")
        print(f"[INFO] Added {added_count} new columns")
        print(f"[INFO] Skipped {skipped_count} existing columns")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("DATABASE MIGRATION: Add nutrition information to foods")
    print("=" * 60)
    print()
    migrate()
