from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from models.education import EducationalContent, ResearchPaper
from database import db
from werkzeug.utils import secure_filename
from utils import parse_markdown, extract_title_from_markdown, allowed_file, save_upload_data, load_upload_data, delete_upload_data
from utils.markdown_utils import MARKDOWN_PROCESSOR
import os
import re
import uuid
from datetime import datetime


def natural_sort_key(chapter_number):
    """
    Sort chapter numbers naturally (1, 2, 2.1, 2.2, 3, 10)
    Converts "2.1" to [2, 1] for proper sorting
    """
    try:
        return [int(part) if part.isdigit() else 0 for part in str(chapter_number).split('.')]
    except:
        return [0]


bp = Blueprint('education', __name__, url_prefix='/education')

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

@bp.route('/')
def index():
    """Educational booklet table of contents"""
    topic = request.args.get('topic')
    search = request.args.get('search')

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

    return render_template('education/index.html', chapters=chapters, current_topic=topic,
                         markdown_available=(MARKDOWN_PROCESSOR is not None))

@bp.route('/chapter/<int:chapter_id>')
def chapter(chapter_id):
    """Individual chapter view"""
    content = EducationalContent.query.get_or_404(chapter_id)
    return render_template('education/chapter.html', content=content)

@bp.route('/upload', methods=['POST'])
def upload_markdown():
    """Upload markdown file and redirect to preview"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.endswith('.md'):
        return jsonify({'error': 'Only .md files are supported'}), 400

    try:
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

        return jsonify({'success': True, 'redirect': url_for('education.preview_upload', upload_id=upload_id)})

    except Exception as e:
        return jsonify({'error': f'{str(e)}'}), 500

@bp.route('/preview_upload', methods=['GET', 'POST'])
def preview_upload():
    """Preview uploaded markdown and allow editing before saving"""

    if request.method == 'GET':
        # Get upload ID from query parameter
        upload_id = request.args.get('upload_id')

        if not upload_id:
            flash('No upload ID provided. Please upload a file first.', 'error')
            return redirect(url_for('education.index'))

        # Load preview data from temporary file
        preview_data = load_upload_data(upload_id)

        if not preview_data:
            flash('No upload data found. Please upload a file first.', 'error')
            return redirect(url_for('education.index'))

        # Convert markdown to HTML for preview
        html_preview = parse_markdown(preview_data['markdown_source'])
        preview_data['html_preview'] = html_preview

        # Get existing chapters for sidebar reference
        existing_chapters = EducationalContent.query.order_by(EducationalContent.order_index).all()
        existing_chapters = sorted(existing_chapters, key=lambda x: natural_sort_key(x.chapter_number))

        # Get unique sections with part numbers (mimic the TOC logic)
        sections_with_parts = []
        seen_sections = {}
        part_counter = 0

        for chapter in existing_chapters:
            chapter_num_str = str(chapter.chapter_number)
            is_roman = chapter_num_str and chapter_num_str[0] in ['i', 'v', 'x']
            is_subchapter = '.' in chapter_num_str and not is_roman

            # Only count main chapters (not roman numerals or subchapters)
            if not is_roman and not is_subchapter and chapter.section:
                if chapter.section not in seen_sections:
                    part_counter += 1
                    seen_sections[chapter.section] = part_counter
                    sections_with_parts.append({
                        'name': chapter.section,
                        'part_number': part_counter
                    })

        return render_template('education/preview.html', data=preview_data, existing_chapters=existing_chapters, sections_with_parts=sections_with_parts, upload_id=upload_id)

    elif request.method == 'POST':
        # Get upload ID from form
        upload_id = request.form.get('upload_id')

        if not upload_id:
            flash('No upload ID provided. Please upload a file first.', 'error')
            return redirect(url_for('education.index'))

        # Load preview data from temporary file
        preview_data = load_upload_data(upload_id)

        if not preview_data:
            flash('No upload data found. Please upload a file first.', 'error')
            return redirect(url_for('education.index'))

        try:
            # Get form data
            chapter_number = request.form.get('chapter_number')
            title = request.form.get('title')
            section = request.form.get('section')
            markdown_source = request.form.get('markdown_source')

            # Convert to HTML
            html_content = parse_markdown(markdown_source)

            # Create new chapter
            chapter = EducationalContent(
                chapter_number=chapter_number,
                section=section,
                title=title,
                content=html_content,
                markdown_source=markdown_source,
                filename=preview_data['filename'],
                is_markdown=True,
                order_index=chapter_number
            )

            db.session.add(chapter)
            db.session.commit()

            # Delete temporary file
            delete_upload_data(upload_id)

            flash(f'Chapter "{title}" added successfully!', 'success')
            return redirect(url_for('education.index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error saving chapter: {str(e)}', 'error')
            return redirect(url_for('education.preview_upload', upload_id=upload_id))

@bp.route('/preview_markdown', methods=['POST'])
def preview_markdown():
    """Convert markdown to HTML for live preview"""
    try:
        md_content = request.json.get('markdown', '')
        html_content = parse_markdown(md_content)
        return jsonify({'html': html_content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/reorder', methods=['POST'])
def reorder_chapters():
    """Update chapter order"""
    try:
        order_data = request.json.get('order', [])

        for item in order_data:
            chapter = EducationalContent.query.get(item['id'])
            if chapter:
                chapter.order_index = item['order']
                chapter.chapter_number = item['chapter_number']

        db.session.commit()
        return jsonify({'success': True})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/edit/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    """Edit chapter markdown"""
    content = EducationalContent.query.get_or_404(chapter_id)

    if request.method == 'POST':
        try:
            md_content = request.form.get('markdown_source')
            custom_title = request.form.get('title')
            custom_chapter_number = request.form.get('chapter_number')

            # Update markdown and HTML
            content.markdown_source = md_content
            content.content = parse_markdown(md_content)
            # Use custom title from form instead of auto-extracting
            content.title = custom_title if custom_title else extract_title_from_markdown(md_content)
            content.section = request.form.get('section', content.section)

            # Update chapter number if provided
            if custom_chapter_number:
                content.chapter_number = custom_chapter_number

            db.session.commit()
            flash('Chapter updated successfully!', 'success')
            return redirect(url_for('education.chapter', chapter_id=chapter_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating chapter: {str(e)}', 'error')

    # Get existing chapters for sidebar reference (excluding current chapter)
    existing_chapters = EducationalContent.query.filter(EducationalContent.id != chapter_id).order_by(EducationalContent.order_index).all()
    existing_chapters = sorted(existing_chapters, key=lambda x: natural_sort_key(x.chapter_number))

    # Get unique sections with part numbers (mimic the TOC logic)
    sections_with_parts = []
    seen_sections = {}
    part_counter = 0

    all_chapters = EducationalContent.query.order_by(EducationalContent.order_index).all()
    all_chapters = sorted(all_chapters, key=lambda x: natural_sort_key(x.chapter_number))

    for chapter in all_chapters:
        chapter_num_str = str(chapter.chapter_number)
        is_roman = chapter_num_str and chapter_num_str[0] in ['i', 'v', 'x']
        is_subchapter = '.' in chapter_num_str and not is_roman

        # Only count main chapters (not roman numerals or subchapters)
        if not is_roman and not is_subchapter and chapter.section:
            if chapter.section not in seen_sections:
                part_counter += 1
                seen_sections[chapter.section] = part_counter
                sections_with_parts.append({
                    'name': chapter.section,
                    'part_number': part_counter
                })

    return render_template('education/edit.html', content=content, existing_chapters=existing_chapters, sections_with_parts=sections_with_parts)

@bp.route('/delete/<int:chapter_id>', methods=['POST'])
def delete_chapter(chapter_id):
    """Delete a chapter"""
    try:
        content = EducationalContent.query.get_or_404(chapter_id)
        db.session.delete(content)
        db.session.commit()
        flash('Chapter deleted successfully!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/upload_image', methods=['POST'])
def upload_image():
    """Upload an image for use in markdown chapters"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, WEBP'}), 400

    try:
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

@bp.route('/research')
def research():
    """Research paper library"""
    papers = ResearchPaper.query.order_by(ResearchPaper.publication_year.desc()).all()
    return render_template('education/research.html', papers=papers)
