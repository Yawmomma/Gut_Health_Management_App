"""
Education Content API Endpoints
================================
API endpoints for educational content management.

Endpoints:
- GET /api/v1/education - List educational chapters with filtering
- GET /api/v1/education/{id} - Get specific chapter
- POST /api/v1/education/upload - Upload markdown file
- POST /api/v1/education - Save chapter after preview
- PUT /api/v1/education/{id} - Update chapter
- DELETE /api/v1/education/{id} - Delete chapter
- POST /api/v1/education/reorder - Reorder chapters
- POST /api/v1/education/images - Upload image for markdown
- POST /api/v1/education/preview-markdown - Convert markdown to HTML
"""

from flask import request, jsonify, current_app
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

from database import db
from models.education import EducationalContent, ResearchPaper
from utils import parse_markdown, extract_title_from_markdown, allowed_file, save_upload_data, load_upload_data, delete_upload_data
from routes.api_v1 import bp
from utils.pagination import paginate_list, get_pagination_params
from utils.validators import ValidationError
from utils.auth import require_api_key, require_scope


def natural_sort_key(chapter_number):
    """
    Sort chapter numbers naturally (1, 2, 2.1, 2.2, 3, 10)
    Converts "2.1" to [2, 1] for proper sorting
    """
    try:
        return [int(part) if part.isdigit() else 0 for part in str(chapter_number).split('.')]
    except:
        return [0]


def save_education_image(file):
    """Save uploaded image and return the path"""
    if file and allowed_file(file.filename):
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        original_filename = secure_filename(file.filename)
        filename = f"edu_{timestamp}_{original_filename}"

        # Save file
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return f"uploads/{filename}"
    return None


# ===========================
# CHAPTER RETRIEVAL ENDPOINTS
# ===========================

@bp.route('/education', methods=['GET'])
@require_api_key
@require_scope('read:education')
def education_list():
    """
    List educational chapters with optional filtering (paginated)

    Query Parameters:
        topic (str): Filter by section/topic
        search (str): Search in title, section, and content
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 50, max: 100)

    Returns:
        JSON with paginated chapters and metadata
        {
            "data": [...],
            "pagination": {...},
            "available_topics": [...],
            "filters": {...}
        }

    Example:
        GET /api/v1/education?topic=FODMAP&search=diet&page=1&per_page=20
    """
    try:
        topic = request.args.get('topic')
        search = request.args.get('search')

        # Get pagination parameters
        try:
            page, per_page = get_pagination_params(request.args, default_per_page=50, max_per_page=100)
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400

        query = EducationalContent.query

        if search:
            # Search in title, section, and content
            search_filter = f'%{search}%'
            query = query.filter(
                (EducationalContent.title.ilike(search_filter)) |
                (EducationalContent.section.ilike(search_filter)) |
                (EducationalContent.content.ilike(search_filter))
            )
        elif topic:
            # Filter by section/topic
            query = query.filter(EducationalContent.section.ilike(f'%{topic}%'))

        chapters = query.order_by(EducationalContent.order_index).all()

        # Sort chapters naturally by chapter number (handles 2.1, 2.2, etc.)
        chapters = sorted(chapters, key=lambda x: natural_sort_key(x.chapter_number))

        # Get unique topics/sections for response metadata
        all_topics = sorted({c.section for c in EducationalContent.query.all() if c.section})

        # Serialize chapters
        chapters_list = []
        for chapter in chapters:
            chapters_list.append({
                'id': chapter.id,
                'chapter_number': chapter.chapter_number,
                'section': chapter.section,
                'title': chapter.title,
                'content': chapter.content,
                'markdown_source': chapter.markdown_source,
                'is_markdown': chapter.is_markdown,
                'filename': chapter.filename,
                'order_index': chapter.order_index,
                'parent_chapter': chapter.parent_chapter,
                'created_at': chapter.created_at.isoformat() if chapter.created_at else None,
                'updated_at': chapter.updated_at.isoformat() if chapter.updated_at else None
            })

        # Apply pagination to serialized list
        result = paginate_list(chapters_list, page=page, per_page=per_page)

        # Add metadata
        result['available_topics'] = all_topics
        result['filters'] = {
            'topic': topic,
            'search': search
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/education/<int:chapter_id>', methods=['GET'])
@require_api_key
@require_scope('read:education')
def education_detail(chapter_id):
    """
    Get specific educational chapter by ID

    Args:
        chapter_id (int): Chapter ID

    Returns:
        JSON object with complete chapter details

    Example:
        GET /api/v1/education/5
    """
    try:
        chapter = EducationalContent.query.get(chapter_id)
        if not chapter:
            return jsonify({'error': f'Chapter with ID {chapter_id} not found'}), 404

        return jsonify({
            'id': chapter.id,
            'chapter_number': chapter.chapter_number,
            'section': chapter.section,
            'title': chapter.title,
            'content': chapter.content,
            'markdown_source': chapter.markdown_source,
            'is_markdown': chapter.is_markdown,
            'filename': chapter.filename,
            'order_index': chapter.order_index,
            'parent_chapter': chapter.parent_chapter,
            'created_at': chapter.created_at.isoformat() if chapter.created_at else None,
            'updated_at': chapter.updated_at.isoformat() if chapter.updated_at else None
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===========================
# CHAPTER CRUD ENDPOINTS
# ===========================

@bp.route('/education/upload', methods=['POST'])
@require_api_key
@require_scope('write:education')
def education_upload():
    """
    Upload markdown file for educational chapter

    Form Data:
        file (file): Markdown file (.md)
        section (str): Chapter section (optional, default: 'General')

    Returns:
        JSON object with upload_id, extracted title, and suggested chapter number

    Example:
        POST /api/v1/education/upload
        Content-Type: multipart/form-data
        file: <markdown file>
        section: FODMAP Basics
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not file.filename.endswith('.md'):
            return jsonify({'error': 'Only .md files are supported'}), 400

        # Read markdown content
        md_content = file.read().decode('utf-8')

        # Extract title
        title = extract_title_from_markdown(md_content)

        # Get next chapter number (find highest main chapter number)
        all_chapters = EducationalContent.query.all()
        next_chapter = "1"  # Default

        if all_chapters:
            # Get all main chapter numbers (without sub-chapters)
            main_chapters = []
            for c in all_chapters:
                if c.chapter_number:
                    try:
                        chapter_str = str(c.chapter_number)
                        # Try to get the main chapter number (before any dot)
                        if '.' in chapter_str:
                            main_num = int(chapter_str.split('.')[0])
                        else:
                            main_num = int(chapter_str)
                        main_chapters.append(main_num)
                    except (ValueError, AttributeError, TypeError):
                        # Skip roman numerals or non-numeric chapter numbers
                        continue

            if main_chapters:
                next_chapter = str(max(main_chapters) + 1)

        # Generate unique upload ID
        upload_id = str(uuid.uuid4())

        # Store data in temporary file
        upload_data = {
            'markdown_source': md_content,
            'filename': secure_filename(file.filename),
            'extracted_title': title,
            'suggested_chapter': next_chapter,
            'section': request.form.get('section', 'General')
        }

        save_upload_data(upload_data, upload_id)

        # Parse markdown for preview
        html_preview = parse_markdown(md_content)

        return jsonify({
            'success': True,
            'upload_id': upload_id,
            'title': title,
            'suggested_chapter': next_chapter,
            'section': upload_data['section'],
            'filename': upload_data['filename'],
            'html_preview': html_preview
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/education', methods=['POST'])
@require_api_key
@require_scope('write:education')
def education_create():
    """
    Save educational chapter after preview

    JSON Body:
        upload_id (str): Upload ID from upload step (optional)
        chapter_number (str): Chapter number (e.g., "1", "2.1")
        title (str): Chapter title
        section (str): Chapter section/topic
        markdown_source (str): Markdown content

    Returns:
        JSON object with created chapter ID

    Example:
        POST /api/v1/education
        {
            "upload_id": "abc-123-def-456",
            "chapter_number": "3",
            "title": "Understanding FODMAPs",
            "section": "FODMAP Basics",
            "markdown_source": "# Understanding FODMAPs\n\n..."
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        upload_id = data.get('upload_id')
        chapter_number = data.get('chapter_number')
        title = data.get('title')
        section = data.get('section')
        markdown_source = data.get('markdown_source')

        if not all([chapter_number, title, section, markdown_source]):
            return jsonify({'error': 'Missing required fields: chapter_number, title, section, markdown_source'}), 400

        # Load upload data if upload_id provided (for filename)
        preview_data = None
        if upload_id:
            preview_data = load_upload_data(upload_id)

        # Convert markdown to HTML
        html_content = parse_markdown(markdown_source)

        # Create new chapter
        chapter = EducationalContent(
            chapter_number=chapter_number,
            section=section,
            title=title,
            content=html_content,
            markdown_source=markdown_source,
            filename=preview_data.get('filename') if preview_data else None,
            is_markdown=True,
            order_index=chapter_number
        )

        db.session.add(chapter)
        db.session.commit()

        # Clean up upload data if it exists
        if upload_id:
            delete_upload_data(upload_id)

        return jsonify({
            'success': True,
            'chapter_id': chapter.id,
            'message': f'Chapter "{title}" added successfully!'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/education/<int:chapter_id>', methods=['PUT'])
@require_api_key
@require_scope('write:education')
def education_update(chapter_id):
    """
    Update existing educational chapter

    Args:
        chapter_id (int): Chapter ID

    JSON Body:
        chapter_number (str): Chapter number (optional)
        title (str): Chapter title
        section (str): Chapter section
        markdown_source (str): Markdown content

    Returns:
        JSON object with success status

    Example:
        PUT /api/v1/education/5
        {
            "chapter_number": "3.1",
            "title": "Updated Chapter Title",
            "section": "FODMAP Basics",
            "markdown_source": "# Updated Content..."
        }
    """
    try:
        chapter = EducationalContent.query.get(chapter_id)
        if not chapter:
            return jsonify({'error': f'Chapter with ID {chapter_id} not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        markdown_source = data.get('markdown_source')
        title = data.get('title')
        section = data.get('section')
        chapter_number = data.get('chapter_number')

        if not all([markdown_source, title, section]):
            return jsonify({'error': 'Missing required fields: title, section, markdown_source'}), 400

        # Update chapter
        chapter.markdown_source = markdown_source
        chapter.content = parse_markdown(markdown_source)
        chapter.title = title
        chapter.section = section

        # Update chapter number if provided
        if chapter_number:
            chapter.chapter_number = chapter_number

        chapter.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Chapter updated successfully!'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/education/<int:chapter_id>', methods=['DELETE'])
@require_api_key
@require_scope('write:education')
def education_delete(chapter_id):
    """
    Delete an educational chapter

    Args:
        chapter_id (int): Chapter ID

    Returns:
        JSON object with success status

    Example:
        DELETE /api/v1/education/5
    """
    try:
        chapter = EducationalContent.query.get(chapter_id)
        if not chapter:
            return jsonify({'error': f'Chapter with ID {chapter_id} not found'}), 404

        db.session.delete(chapter)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Chapter deleted successfully!'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/education/reorder', methods=['POST'])
@require_api_key
@require_scope('write:education')
def education_reorder():
    """
    Update chapter order and chapter numbers

    JSON Body:
        order (array): Array of objects with id, order, and chapter_number
            [
                {"id": 1, "order": 1, "chapter_number": "1"},
                {"id": 2, "order": 2, "chapter_number": "2"},
                {"id": 3, "order": 3, "chapter_number": "2.1"}
            ]

    Returns:
        JSON object with success status

    Example:
        POST /api/v1/education/reorder
        {
            "order": [
                {"id": 1, "order": 1, "chapter_number": "1"},
                {"id": 3, "order": 2, "chapter_number": "2"},
                {"id": 2, "order": 3, "chapter_number": "3"}
            ]
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        order_data = data.get('order', [])
        if not order_data:
            return jsonify({'error': 'Order array is required'}), 400

        for item in order_data:
            if not all(k in item for k in ['id', 'order', 'chapter_number']):
                return jsonify({'error': 'Each order item must have id, order, and chapter_number'}), 400

            chapter = EducationalContent.query.get(item['id'])
            if chapter:
                chapter.order_index = item['order']
                chapter.chapter_number = item['chapter_number']

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Chapters reordered successfully!'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ===========================
# UTILITY ENDPOINTS
# ===========================

@bp.route('/education/images', methods=['POST'])
@require_api_key
@require_scope('write:education')
def education_upload_image():
    """
    Upload an image for use in markdown chapters

    Form Data:
        image (file): Image file (PNG, JPG, JPEG, GIF, WEBP)

    Returns:
        JSON object with image path and markdown syntax

    Example:
        POST /api/v1/education/images
        Content-Type: multipart/form-data
        image: <image file>
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['image']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, WEBP'}), 400

        image_path = save_education_image(file)
        if image_path:
            # Return the markdown syntax for the image
            markdown_syntax = f"![Image description](/{image_path})"
            return jsonify({
                'success': True,
                'path': f"/{image_path}",
                'markdown': markdown_syntax,
                'filename': file.filename
            })
        else:
            return jsonify({'error': 'Failed to save image'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/education/preview-markdown', methods=['POST'])
@require_api_key
@require_scope('read:education')
def education_preview_markdown():
    """
    Convert markdown to HTML for live preview

    JSON Body:
        markdown (str): Markdown content to convert

    Returns:
        JSON object with rendered HTML

    Example:
        POST /api/v1/education/preview-markdown
        {
            "markdown": "# Heading\n\nSome **bold** text."
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        markdown_content = data.get('markdown', '')
        html_content = parse_markdown(markdown_content)

        return jsonify({
            'html': html_content
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
