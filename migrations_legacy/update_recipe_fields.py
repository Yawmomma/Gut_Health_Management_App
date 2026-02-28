"""
Database migration to update recipe fields
- Remove main_ingredient column
- Increase preparation_method and occasion column sizes to support comma-separated lists
"""

import sqlite3
import os

def migrate():
    """Run the migration"""
    db_path = os.path.join('instance', 'gut_health.db')

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if main_ingredient column exists
        cursor.execute("PRAGMA table_info(recipes)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        print("Current columns:", column_names)

        if 'main_ingredient' in column_names:
            print("Removing main_ingredient column...")

            # SQLite doesn't support DROP COLUMN directly, so we need to:
            # 1. Create a new table without main_ingredient
            # 2. Copy data from old table
            # 3. Drop old table
            # 4. Rename new table

            # Get the current table schema
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='recipes'")
            create_sql = cursor.fetchone()[0]
            print(f"Current table schema:\n{create_sql}\n")

            # Drop recipes_new table if it exists (from failed migration)
            cursor.execute("DROP TABLE IF EXISTS recipes_new")

            # Create new table without main_ingredient
            cursor.execute("""
                CREATE TABLE recipes_new (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    servings INTEGER DEFAULT 1,
                    prep_time VARCHAR(50),
                    cook_time VARCHAR(50),
                    instructions TEXT,
                    notes TEXT,
                    category VARCHAR(100),
                    subcategory VARCHAR(200),
                    cuisine VARCHAR(100),
                    dietary_needs VARCHAR(200),
                    preparation_method VARCHAR(200),
                    occasion VARCHAR(200),
                    difficulty VARCHAR(50),
                    tags VARCHAR(500),
                    image_path VARCHAR(500),
                    source_url VARCHAR(500),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Copy data from old table (excluding main_ingredient)
            # Handle source_url column which may or may not exist
            if 'source_url' in column_names:
                cursor.execute("""
                    INSERT INTO recipes_new
                    (id, name, description, servings, prep_time, cook_time, instructions, notes,
                     category, subcategory, cuisine, dietary_needs, preparation_method, occasion,
                     difficulty, tags, image_path, source_url, created_at, updated_at)
                    SELECT
                     id, name, description, servings, prep_time, cook_time, instructions, notes,
                     category, subcategory, cuisine, dietary_needs, preparation_method, occasion,
                     difficulty, tags, image_path, source_url, created_at, updated_at
                    FROM recipes
                """)
            else:
                cursor.execute("""
                    INSERT INTO recipes_new
                    (id, name, description, servings, prep_time, cook_time, instructions, notes,
                     category, subcategory, cuisine, dietary_needs, preparation_method, occasion,
                     difficulty, tags, image_path, created_at, updated_at)
                    SELECT
                     id, name, description, servings, prep_time, cook_time, instructions, notes,
                     category, subcategory, cuisine, dietary_needs, preparation_method, occasion,
                     difficulty, tags, image_path, created_at, updated_at
                    FROM recipes
                """)

            # Drop old table
            cursor.execute("DROP TABLE recipes")

            # Rename new table
            cursor.execute("ALTER TABLE recipes_new RENAME TO recipes")

            print("[OK] Successfully removed main_ingredient column")
            print("[OK] Updated preparation_method to VARCHAR(200)")
            print("[OK] Updated occasion to VARCHAR(200)")
        else:
            print("main_ingredient column not found - already removed or never existed")

        conn.commit()
        print("\nMigration completed successfully!")

    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
