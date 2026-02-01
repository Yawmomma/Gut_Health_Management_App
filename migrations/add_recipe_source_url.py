from database import db


def upgrade():
    """Add source_url column to recipes table."""
    conn = db.engine.connect()
    conn.execute('ALTER TABLE recipes ADD COLUMN source_url VARCHAR(500)')
    conn.close()


if __name__ == '__main__':
    upgrade()
