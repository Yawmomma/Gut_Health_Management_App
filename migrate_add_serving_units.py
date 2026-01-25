"""
Migration script to add serving unit columns to the foods table
Run this once to update your existing database
"""
import sqlite3
import os
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Path to your database
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'gut_health.db')

# Check if database exists
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    print("The columns will be created automatically when you first run the app.")
    exit(0)

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if columns already exist
cursor.execute("PRAGMA table_info(foods)")
columns = [column[1] for column in cursor.fetchall()]

columns_to_add = [
    ('safe_serving_unit', 'VARCHAR(20)'),
    ('moderate_serving_unit', 'VARCHAR(20)'),
    ('high_serving_unit', 'VARCHAR(20)')
]

added_columns = []
for column_name, column_type in columns_to_add:
    if column_name not in columns:
        try:
            cursor.execute(f"ALTER TABLE foods ADD COLUMN {column_name} {column_type}")
            added_columns.append(column_name)
            print(f"✓ Added column: {column_name}")
        except sqlite3.Error as e:
            print(f"✗ Error adding {column_name}: {e}")
    else:
        print(f"○ Column {column_name} already exists")

# Commit changes
conn.commit()

# Set default value of 'g' for existing records that have serving sizes but no units
if added_columns:
    print("\nSetting default unit 'g' for existing food items...")
    try:
        # Only update rows where serving size exists but unit is NULL
        cursor.execute("""
            UPDATE foods
            SET safe_serving_unit = 'g'
            WHERE safe_serving IS NOT NULL
            AND safe_serving != ''
            AND safe_serving_unit IS NULL
        """)
        cursor.execute("""
            UPDATE foods
            SET moderate_serving_unit = 'g'
            WHERE moderate_serving IS NOT NULL
            AND moderate_serving != ''
            AND moderate_serving_unit IS NULL
        """)
        cursor.execute("""
            UPDATE foods
            SET high_serving_unit = 'g'
            WHERE high_serving IS NOT NULL
            AND high_serving != ''
            AND high_serving_unit IS NULL
        """)
        conn.commit()
        print("✓ Default units set successfully")
    except sqlite3.Error as e:
        print(f"✗ Error setting default units: {e}")

# Close connection
conn.close()

if added_columns:
    print(f"\n✅ Migration complete! Added {len(added_columns)} column(s).")
else:
    print("\n✅ No migration needed - all columns already exist.")

print("\nYou can now restart your Flask app.")
