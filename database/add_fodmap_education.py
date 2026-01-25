"""
Add FODMAP Educational Guide to the database
"""
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models.education import EducationalContent
import markdown2

def convert_markdown_to_html(md_text):
    """Convert markdown to HTML with extras for better formatting"""
    return markdown2.markdown(md_text, extras=[
        'fenced-code-blocks',
        'tables',
        'header-ids',
        'toc',
        'break-on-newline'
    ])

def add_fodmap_guide():
    """Add the FODMAP educational guide as Chapter 1"""

    # Read the markdown file from docs folder
    md_file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'docs',
        'educational_content',
        'FODMAP_Guide.md'
    )

    if not os.path.exists(md_file_path):
        print(f"Error: File not found at {md_file_path}")
        return False

    with open(md_file_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    # Convert to HTML
    html_content = convert_markdown_to_html(markdown_content)

    with app.app_context():
        # Check if Chapter 1 already exists
        existing = EducationalContent.query.filter_by(chapter_number=1).first()

        if existing:
            print("Chapter 1 already exists. Updating...")
            existing.title = "Understanding FODMAPs: A Complete Educational Guide"
            existing.section = "FODMAPs"
            existing.content = html_content
            existing.order_index = 1
            print("✓ Chapter 1 updated successfully!")
        else:
            print("Adding Chapter 1: FODMAP Educational Guide...")
            chapter = EducationalContent(
                chapter_number=1,
                section="FODMAPs",
                title="Understanding FODMAPs: A Complete Educational Guide",
                content=html_content,
                order_index=1
            )
            db.session.add(chapter)
            print("✓ Chapter 1 added successfully!")

        db.session.commit()

        # Show summary
        total_chapters = EducationalContent.query.count()
        print(f"\n📚 Total chapters in database: {total_chapters}")
        print("\nTo view the educational content, run the app and navigate to:")
        print("http://localhost:5000/education")

        return True

if __name__ == '__main__':
    print("=" * 60)
    print("ADDING FODMAP EDUCATIONAL GUIDE TO DATABASE")
    print("=" * 60)

    success = add_fodmap_guide()

    if success:
        print("\n✓ FODMAP Educational Guide added successfully!")
    else:
        print("\n✗ Failed to add FODMAP Educational Guide")
        sys.exit(1)
