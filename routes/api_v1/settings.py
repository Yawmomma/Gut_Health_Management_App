"""
Settings & Help Document API Endpoints
=======================================
API endpoints for settings, database operations, and help documents.

Endpoints:
Database Operations:
- GET /api/v1/settings/backup - Download database backup
- GET /api/v1/settings/integrity-check - Get database integrity issues
- POST /api/v1/settings/integrity-check/fix - Fix database integrity issues

Help Documents:
- GET /api/v1/help - List help documents with filtering
- GET /api/v1/help/{id} - Get specific help document
- POST /api/v1/help/upload - Upload markdown file for help document
- POST /api/v1/help - Save help document after preview
- PUT /api/v1/help/{id} - Update help document
- DELETE /api/v1/help/{id} - Delete help document
- POST /api/v1/help/preview-markdown - Convert markdown to HTML for preview
"""

from flask import request, jsonify, send_file, current_app
import os
import uuid
from datetime import datetime, timezone
from werkzeug.utils import secure_filename

from database import db
from models.diary import DiaryEntry, Meal, MealFood, Symptom, BowelMovement, StressLog, Note
from models.food import Food
from models.recipe import Recipe, RecipeIngredient, SavedMeal, SavedMealItem
from models.education import HelpDocument
from utils import parse_markdown, extract_title_from_markdown, save_upload_data, load_upload_data, delete_upload_data
from routes.api_v1 import bp
from utils.auth import require_api_key, require_scope

# Helper constants
HELP_UPLOAD_SUBDIR = 'help_uploads'


# ===========================
# HELPER FUNCTIONS FOR INTEGRITY CHECKS
# ===========================

def get_orphaned_meal_foods_query():
    """Query for MealFood records with no parent Meal."""
    return db.session.query(MealFood).filter(
        ~db.session.query(Meal).filter(Meal.id == MealFood.meal_id).exists()
    )

def get_orphaned_recipe_ingredients_query():
    """Query for RecipeIngredient records with no parent Recipe."""
    return db.session.query(RecipeIngredient).filter(
        ~db.session.query(Recipe).filter(Recipe.id == RecipeIngredient.recipe_id).exists()
    )

def get_orphaned_saved_meal_items_query():
    """Query for SavedMealItem records with no parent SavedMeal."""
    return db.session.query(SavedMealItem).filter(
        ~db.session.query(SavedMeal).filter(SavedMeal.id == SavedMealItem.saved_meal_id).exists()
    )

def get_invalid_meal_foods_query():
    """Query for MealFood records pointing to deleted Food."""
    return db.session.query(MealFood).filter(
        ~db.session.query(Food).filter(Food.id == MealFood.food_id).exists()
    )

def get_invalid_recipe_ingredients_query():
    """Query for RecipeIngredient records pointing to deleted Food."""
    return db.session.query(RecipeIngredient).filter(
        ~db.session.query(Food).filter(Food.id == RecipeIngredient.food_id).exists()
    )

def get_invalid_saved_meal_items_query():
    """Query for SavedMealItem records pointing to deleted Food."""
    return db.session.query(SavedMealItem).filter(
        ~db.session.query(Food).filter(Food.id == SavedMealItem.food_id).exists()
    )

def get_empty_diary_entries():
    """Get DiaryEntry records with no related content."""
    empty = []
    for entry in DiaryEntry.query.all():
        if not (entry.meals or entry.symptoms or entry.bowel_movements or
                entry.stress_logs or entry.notes):
            empty.append(entry)
    return empty


# ===========================
# DATABASE OPERATIONS ENDPOINTS
# ===========================

@bp.route('/settings/backup', methods=['GET'])
@require_api_key
@require_scope('admin:backup')
def settings_backup():
    """
    Download a backup of the database

    Returns:
        SQLite database file with timestamped filename

    Example:
        GET /api/v1/settings/backup
    """
    try:
        # Use Flask's instance_path for correct absolute path
        db_path = os.path.join(current_app.instance_path, 'gut_health.db')

        if not os.path.exists(db_path):
            return jsonify({'error': 'Database file not found'}), 404

        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'gut_health_backup_{timestamp}.db'

        # Send file to user
        return send_file(
            db_path,
            as_attachment=True,
            download_name=backup_filename,
            mimetype='application/x-sqlite3'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/settings/integrity-check', methods=['GET'])
@require_api_key
@require_scope('admin:settings')
def settings_integrity_check():
    """
    Run database integrity checks and return issues

    Returns:
        JSON object with array of issues found:
        - Orphaned MealFood records
        - Orphaned RecipeIngredient records
        - Orphaned SavedMealItem records
        - Empty DiaryEntry records
        - Invalid food references in meals
        - Invalid food references in recipes
        - Invalid food references in saved meals
        - Orphaned photo files

    Example:
        GET /api/v1/settings/integrity-check
    """
    try:
        issues = []

        # Check 1: Orphaned MealFood records
        orphaned_meal_foods = get_orphaned_meal_foods_query().count()
        if orphaned_meal_foods > 0:
            issues.append({
                'type': 'Orphaned Meal-Food Links',
                'count': orphaned_meal_foods,
                'description': 'MealFood records with no parent Meal',
                'severity': 'warning'
            })

        # Check 2: Orphaned RecipeIngredient records
        orphaned_recipe_ingredients = get_orphaned_recipe_ingredients_query().count()
        if orphaned_recipe_ingredients > 0:
            issues.append({
                'type': 'Orphaned Recipe Ingredients',
                'count': orphaned_recipe_ingredients,
                'description': 'RecipeIngredient records with no parent Recipe',
                'severity': 'warning'
            })

        # Check 3: Orphaned SavedMealItem records
        orphaned_saved_meal_items = get_orphaned_saved_meal_items_query().count()
        if orphaned_saved_meal_items > 0:
            issues.append({
                'type': 'Orphaned Saved Meal Items',
                'count': orphaned_saved_meal_items,
                'description': 'SavedMealItem records with no parent SavedMeal',
                'severity': 'warning'
            })

        # Check 4: DiaryEntry with no related content
        orphaned_entries_count = len(get_empty_diary_entries())
        if orphaned_entries_count > 0:
            issues.append({
                'type': 'Empty Diary Entries',
                'count': orphaned_entries_count,
                'description': 'DiaryEntry records with no related content',
                'severity': 'info'
            })

        # Check 5: MealFood pointing to deleted Food
        invalid_meal_foods = get_invalid_meal_foods_query().count()
        if invalid_meal_foods > 0:
            issues.append({
                'type': 'Invalid Meal-Food References',
                'count': invalid_meal_foods,
                'description': 'MealFood records pointing to deleted Food items',
                'severity': 'danger'
            })

        # Check 6: RecipeIngredient pointing to deleted Food
        invalid_recipe_ingredients = get_invalid_recipe_ingredients_query().count()
        if invalid_recipe_ingredients > 0:
            issues.append({
                'type': 'Invalid Recipe Ingredient References',
                'count': invalid_recipe_ingredients,
                'description': 'RecipeIngredient records pointing to deleted Food items',
                'severity': 'danger'
            })

        # Check 7: SavedMealItem pointing to deleted Food
        invalid_saved_meal_items = get_invalid_saved_meal_items_query().count()
        if invalid_saved_meal_items > 0:
            issues.append({
                'type': 'Invalid Saved Meal Item References',
                'count': invalid_saved_meal_items,
                'description': 'SavedMealItem records pointing to deleted Food items',
                'severity': 'danger'
            })

        # Check 8: Orphaned photo files
        orphaned_photos = []
        uploads_dir = os.path.join('static', 'uploads')
        if os.path.exists(uploads_dir):
            # Get all photo files
            photo_files = []
            for filename in os.listdir(uploads_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    photo_files.append(filename)

            # Get all photos referenced in database
            db_photos = set()
            for recipe in Recipe.query.all():
                if recipe.image_path:
                    db_photos.add(os.path.basename(recipe.image_path))
            for meal in SavedMeal.query.all():
                if meal.image_path:
                    db_photos.add(os.path.basename(meal.image_path))

            # Find orphaned photos
            for photo in photo_files:
                if photo not in db_photos:
                    orphaned_photos.append(photo)

            if orphaned_photos:
                issues.append({
                    'type': 'Orphaned Photo Files',
                    'count': len(orphaned_photos),
                    'description': 'Photo files in uploads folder with no database record',
                    'severity': 'info',
                    'details': orphaned_photos[:10]  # Show first 10
                })

        return jsonify({
            'issues': issues,
            'total_issues': len(issues),
            'has_critical': any(issue['severity'] == 'danger' for issue in issues)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/settings/integrity-check/fix', methods=['POST'])
@require_api_key
@require_scope('admin:settings')
def settings_integrity_check_fix():
    """
    Auto-fix database integrity issues

    Fixes:
    - Deletes orphaned MealFood records
    - Deletes orphaned RecipeIngredient records
    - Deletes orphaned SavedMealItem records
    - Deletes empty DiaryEntry records

    Returns:
        JSON object with count of fixed records

    Example:
        POST /api/v1/settings/integrity-check/fix
    """
    try:
        fixed_count = 0

        # Fix orphaned MealFood records
        for mf in get_orphaned_meal_foods_query().all():
            db.session.delete(mf)
            fixed_count += 1

        # Fix orphaned RecipeIngredient records
        for ri in get_orphaned_recipe_ingredients_query().all():
            db.session.delete(ri)
            fixed_count += 1

        # Fix orphaned SavedMealItem records
        for smi in get_orphaned_saved_meal_items_query().all():
            db.session.delete(smi)
            fixed_count += 1

        # Fix orphaned DiaryEntry records
        for entry in get_empty_diary_entries():
            db.session.delete(entry)
            fixed_count += 1

        db.session.commit()

        return jsonify({
            'success': True,
            'fixed_count': fixed_count,
            'message': f'Fixed {fixed_count} orphaned record(s) successfully!'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ===========================
# HELP DOCUMENT ENDPOINTS
# ===========================

@bp.route('/help', methods=['GET'])
@require_api_key
@require_scope('read:help')
def help_list():
    """
    List help documents with optional filtering

    Query Parameters:
        category (str): Filter by category
        search (str): Search in title, category, and content

    Returns:
        JSON array of help documents with metadata

    Example:
        GET /api/v1/help?category=Getting Started&search=recipe
    """
    try:
        category = request.args.get('category')
        search = request.args.get('search')

        # Query database for help documents
        query = HelpDocument.query

        if search:
            search_filter = f'%{search}%'
            query = query.filter(
                (HelpDocument.title.ilike(search_filter)) |
                (HelpDocument.category.ilike(search_filter)) |
                (HelpDocument.content.ilike(search_filter))
            )
        elif category:
            query = query.filter(HelpDocument.category == category)

        documents = query.order_by(HelpDocument.category, HelpDocument.order_index, HelpDocument.title).all()

        # Get unique categories for response metadata
        all_categories = sorted({doc.category for doc in HelpDocument.query.all() if doc.category})

        # Serialize documents
        docs_list = []
        for doc in documents:
            docs_list.append({
                'id': doc.id,
                'title': doc.title,
                'category': doc.category,
                'content': doc.content,
                'markdown_source': doc.markdown_source,
                'is_markdown': doc.is_markdown,
                'order_index': doc.order_index,
                'created_at': doc.created_at.isoformat() if doc.created_at else None,
                'updated_at': doc.updated_at.isoformat() if doc.updated_at else None
            })

        return jsonify({
            'documents': docs_list,
            'count': len(docs_list),
            'categories': all_categories,
            'filters': {
                'category': category,
                'search': search
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/help/<int:doc_id>', methods=['GET'])
@require_api_key
@require_scope('read:help')
def help_detail(doc_id):
    """
    Get specific help document by ID

    Args:
        doc_id (int): Help document ID

    Returns:
        JSON object with complete help document details

    Example:
        GET /api/v1/help/5
    """
    try:
        document = HelpDocument.query.get(doc_id)
        if not document:
            return jsonify({'error': f'Help document with ID {doc_id} not found'}), 404

        return jsonify({
            'id': document.id,
            'title': document.title,
            'category': document.category,
            'content': document.content,
            'markdown_source': document.markdown_source,
            'is_markdown': document.is_markdown,
            'filename': document.filename,
            'order_index': document.order_index,
            'created_at': document.created_at.isoformat() if document.created_at else None,
            'updated_at': document.updated_at.isoformat() if document.updated_at else None
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/help/upload', methods=['POST'])
@require_api_key
@require_scope('write:help')
def help_upload():
    """
    Upload markdown file for help document

    Form Data:
        file (file): Markdown file (.md)
        category (str): Document category (optional, default: 'General')

    Returns:
        JSON object with upload_id for preview step

    Example:
        POST /api/v1/help/upload
        Content-Type: multipart/form-data
        file: <markdown file>
        category: Getting Started
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not file.filename.endswith('.md'):
            return jsonify({'error': 'Only .md files are supported'}), 400

        md_content = file.read().decode('utf-8')
        title = extract_title_from_markdown(md_content)
        upload_id = str(uuid.uuid4())

        upload_data = {
            'markdown_source': md_content,
            'filename': secure_filename(file.filename),
            'extracted_title': title,
            'category': request.form.get('category', 'General')
        }

        save_upload_data(upload_data, upload_id, HELP_UPLOAD_SUBDIR)

        # Parse markdown for preview
        html_preview = parse_markdown(md_content)

        return jsonify({
            'success': True,
            'upload_id': upload_id,
            'title': title,
            'category': upload_data['category'],
            'filename': upload_data['filename'],
            'html_preview': html_preview
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/help', methods=['POST'])
@require_api_key
@require_scope('write:help')
def help_create():
    """
    Save help document after preview

    JSON Body:
        upload_id (str): Upload ID from upload step
        title (str): Document title
        category (str): Document category
        markdown_source (str): Markdown content

    Returns:
        JSON object with created document ID

    Example:
        POST /api/v1/help
        {
            "upload_id": "abc-123-def-456",
            "title": "Getting Started Guide",
            "category": "Getting Started",
            "markdown_source": "# Welcome\n\nThis is the guide..."
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        upload_id = data.get('upload_id')
        title = data.get('title')
        category = data.get('category')
        markdown_source = data.get('markdown_source')

        if not all([title, category, markdown_source]):
            return jsonify({'error': 'Missing required fields: title, category, markdown_source'}), 400

        # Load upload data if upload_id provided (for filename)
        preview_data = None
        if upload_id:
            preview_data = load_upload_data(upload_id, HELP_UPLOAD_SUBDIR)

        # Calculate next order index for this category
        category_docs = HelpDocument.query.filter_by(category=category).all()
        max_order = max([doc.order_index for doc in category_docs], default=0)

        # Convert markdown to HTML
        html_content = parse_markdown(markdown_source)

        # Create new help document in database
        document = HelpDocument(
            category=category,
            title=title,
            content=html_content,
            markdown_source=markdown_source,
            filename=preview_data.get('filename') if preview_data else None,
            is_markdown=True,
            order_index=max_order + 1
        )

        db.session.add(document)
        db.session.commit()

        # Clean up upload data if it exists
        if upload_id:
            delete_upload_data(upload_id, HELP_UPLOAD_SUBDIR)

        return jsonify({
            'success': True,
            'document_id': document.id,
            'message': f'Help document "{title}" added successfully!'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/help/<int:doc_id>', methods=['PUT'])
@require_api_key
@require_scope('write:help')
def help_update(doc_id):
    """
    Update existing help document

    Args:
        doc_id (int): Help document ID

    JSON Body:
        title (str): Document title
        category (str): Document category
        markdown_source (str): Markdown content

    Returns:
        JSON object with success status

    Example:
        PUT /api/v1/help/5
        {
            "title": "Updated Guide",
            "category": "Getting Started",
            "markdown_source": "# Updated Content..."
        }
    """
    try:
        document = HelpDocument.query.get(doc_id)
        if not document:
            return jsonify({'error': f'Help document with ID {doc_id} not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        markdown_source = data.get('markdown_source')
        title = data.get('title')
        category = data.get('category')

        if not all([markdown_source, title, category]):
            return jsonify({'error': 'Missing required fields: title, category, markdown_source'}), 400

        # Update document
        document.markdown_source = markdown_source
        document.content = parse_markdown(markdown_source)
        document.title = title

        # If category changed, recalculate order index
        if document.category != category:
            document.category = category
            category_docs = HelpDocument.query.filter_by(category=category).all()
            max_order = max([doc.order_index for doc in category_docs], default=0)
            document.order_index = max_order + 1

        document.updated_at = datetime.now(timezone.utc)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Help document updated successfully!'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/help/<int:doc_id>', methods=['DELETE'])
@require_api_key
@require_scope('write:help')
def help_delete(doc_id):
    """
    Delete a help document

    Args:
        doc_id (int): Help document ID

    Returns:
        JSON object with success status

    Example:
        DELETE /api/v1/help/5
    """
    try:
        document = HelpDocument.query.get(doc_id)
        if not document:
            return jsonify({'error': f'Help document with ID {doc_id} not found'}), 404

        db.session.delete(document)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Help document deleted successfully!'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/help/preview-markdown', methods=['POST'])
@require_api_key
@require_scope('read:help')
def help_preview_markdown():
    """
    Convert markdown to HTML for live preview

    JSON Body:
        markdown (str): Markdown content to convert

    Returns:
        JSON object with rendered HTML

    Example:
        POST /api/v1/help/preview-markdown
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
