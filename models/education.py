from database import db
from datetime import datetime

class EducationalContent(db.Model):
    """Educational booklet chapters and content"""
    __tablename__ = 'educational_content'

    id = db.Column(db.Integer, primary_key=True)
    chapter_number = db.Column(db.String(20), nullable=False)  # Changed to String to support "2.1", "2.2" format
    section = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text, nullable=False)

    # Markdown support
    markdown_source = db.Column(db.Text)  # Original markdown content
    filename = db.Column(db.String(500))  # Original filename
    is_markdown = db.Column(db.Boolean, default=False)

    # Optional metadata
    order_index = db.Column(db.Integer)
    parent_chapter = db.Column(db.Integer)  # For sub-sections

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<EducationalContent Chapter {self.chapter_number}: {self.title}>'


class ResearchPaper(db.Model):
    """Research paper repository"""
    __tablename__ = 'research_papers'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    authors = db.Column(db.String(500))
    journal = db.Column(db.String(200))
    publication_year = db.Column(db.Integer)

    topic = db.Column(db.String(100))  # FODMAPs, Histamine, Vagus Nerve, etc.
    abstract = db.Column(db.Text)
    key_findings = db.Column(db.Text)
    relevance_notes = db.Column(db.Text)

    pdf_path = db.Column(db.String(500))  # Path to PDF file
    external_url = db.Column(db.String(500))

    star_rating = db.Column(db.Integer)  # 1-5 stars for personal relevance

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ResearchPaper {self.title}>'


class UserBookmark(db.Model):
    """Bookmarks for educational content"""
    __tablename__ = 'user_bookmarks'

    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey('educational_content.id'), nullable=False)
    user_note = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    content = db.relationship('EducationalContent')

    def __repr__(self):
        return f'<Bookmark for content {self.content_id}>'


class HelpDocument(db.Model):
    """Help documents, FAQs, tips, and navigation guides"""
    __tablename__ = 'help_documents'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)  # FAQ, Tips, Navigation, etc.
    title = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text, nullable=False)

    # Markdown support
    markdown_source = db.Column(db.Text)
    filename = db.Column(db.String(500))
    is_markdown = db.Column(db.Boolean, default=False)

    # Ordering
    order_index = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<HelpDocument {self.category}: {self.title}>'
