"""
Migration: Add persona field to chat_conversations table
Date: 2026-02-01
"""

import sqlite3
import os

def migrate():
    """Add persona column to chat_conversations table"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'gut_health.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(chat_conversations)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'persona' not in columns:
            # Add persona column with default value
            cursor.execute("""
                ALTER TABLE chat_conversations
                ADD COLUMN persona VARCHAR(50) DEFAULT 'nutritionist'
            """)
            print("+ Added 'persona' column to chat_conversations table")

            # Update existing rows to have the default persona
            cursor.execute("""
                UPDATE chat_conversations
                SET persona = 'nutritionist'
                WHERE persona IS NULL
            """)
            print("+ Set default persona for existing conversations")
        else:
            print("+ 'persona' column already exists, skipping")

        conn.commit()
        print("\n+ Migration completed successfully!")

    except Exception as e:
        conn.rollback()
        print(f"\n- Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
