"""
Migration script to convert chapter_number from Integer to String
This allows support for sub-chapters (e.g., 2.1, 2.2)

Run this once after updating the model:
python migrate_chapter_numbers.py
"""

from app import app, db
from models.education import EducationalContent
from sqlalchemy import text

def migrate_chapter_numbers():
    """Convert chapter_number from INTEGER to VARCHAR"""
    with app.app_context():
        try:
            # Check if we need to migrate
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('educational_content')
            chapter_num_col = next((col for col in columns if col['name'] == 'chapter_number'), None)

            if chapter_num_col and 'INTEGER' in str(chapter_num_col['type']).upper():
                print("📋 Starting migration: Converting chapter_number from INTEGER to VARCHAR...")

                # For SQLite, we need to recreate the table
                print("   Creating backup of data...")
                chapters = EducationalContent.query.all()
                chapter_data = [(c.id, str(c.chapter_number), c.section, c.title, c.content,
                                c.markdown_source, c.filename, c.is_markdown, c.order_index,
                                c.parent_chapter, c.created_at, c.updated_at) for c in chapters]

                print(f"   Backed up {len(chapter_data)} chapters")

                # Drop and recreate table
                print("   Recreating table with new schema...")
                db.session.execute(text('DROP TABLE IF EXISTS educational_content'))
                db.session.commit()

                # Recreate tables
                db.create_all()

                # Restore data
                print("   Restoring data with string chapter numbers...")
                for data in chapter_data:
                    chapter = EducationalContent(
                        id=data[0],
                        chapter_number=data[1],  # Now a string
                        section=data[2],
                        title=data[3],
                        content=data[4],
                        markdown_source=data[5],
                        filename=data[6],
                        is_markdown=data[7],
                        order_index=data[8],
                        parent_chapter=data[9],
                        created_at=data[10],
                        updated_at=data[11]
                    )
                    db.session.add(chapter)

                db.session.commit()
                print("✅ Migration complete! Chapter numbers are now strings.")
                print("   You can now use sub-chapters like '2.1', '2.2', etc.")

            else:
                print("✅ No migration needed. Chapter number is already a string type.")

        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    print("=" * 60)
    print("CHAPTER NUMBER MIGRATION SCRIPT")
    print("=" * 60)
    migrate_chapter_numbers()
    print("=" * 60)
