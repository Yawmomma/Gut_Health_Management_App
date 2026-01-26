from flask import Blueprint, render_template, send_file, flash, redirect, url_for, request, jsonify, current_app
import os
import shutil
import json
import tempfile
import uuid
import re
from datetime import datetime
from werkzeug.utils import secure_filename
from database import db
from models.diary import DiaryEntry, Meal, MealFood, Symptom, BowelMovement, StressLog, Note
from models.food import Food
from models.recipe import Recipe, RecipeIngredient, SavedMeal, SavedMealItem

bp = Blueprint('settings', __name__, url_prefix='/settings')

@bp.route('/')
def index():
    """Settings page"""
    # Get database file info using Flask's instance_path
    db_path = os.path.join(current_app.instance_path, 'gut_health.db')
    db_exists = os.path.exists(db_path)

    db_info = None
    if db_exists:
        db_size = os.path.getsize(db_path)
        db_modified = datetime.fromtimestamp(os.path.getmtime(db_path))
        db_info = {
            'size': db_size,
            'size_mb': round(db_size / (1024 * 1024), 2),
            'modified': db_modified,
            'path': db_path
        }

    return render_template('settings/index.html', db_info=db_info)

@bp.route('/tags')
def tags():
    """Tags management page"""
    return render_template('settings/tags.html')

@bp.route('/integrity-check', methods=['GET', 'POST'])
def integrity_check():
    """Database integrity check page"""
    issues = []

    if request.method == 'POST' and request.form.get('action') == 'fix':
        # Auto-fix orphaned records
        try:
            fixed_count = 0

            # Fix orphaned MealFood records
            orphaned_meal_foods = db.session.query(MealFood).filter(
                ~db.session.query(Meal).filter(Meal.id == MealFood.meal_id).exists()
            ).all()
            for mf in orphaned_meal_foods:
                db.session.delete(mf)
                fixed_count += 1

            # Fix orphaned RecipeIngredient records
            orphaned_recipe_ingredients = db.session.query(RecipeIngredient).filter(
                ~db.session.query(Recipe).filter(Recipe.id == RecipeIngredient.recipe_id).exists()
            ).all()
            for ri in orphaned_recipe_ingredients:
                db.session.delete(ri)
                fixed_count += 1

            # Fix orphaned SavedMealItem records
            orphaned_saved_meal_items = db.session.query(SavedMealItem).filter(
                ~db.session.query(SavedMeal).filter(SavedMeal.id == SavedMealItem.saved_meal_id).exists()
            ).all()
            for smi in orphaned_saved_meal_items:
                db.session.delete(smi)
                fixed_count += 1

            # Fix orphaned DiaryEntry records (entries with no related content)
            all_entries = DiaryEntry.query.all()
            for entry in all_entries:
                has_content = (
                    entry.meals or
                    entry.symptoms or
                    entry.bowel_movements or
                    entry.stress_logs or
                    entry.notes
                )
                if not has_content:
                    db.session.delete(entry)
                    fixed_count += 1

            db.session.commit()
            flash(f'Fixed {fixed_count} orphaned record(s) successfully!', 'success')
            return redirect(url_for('settings.integrity_check'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error fixing records: {str(e)}', 'error')

    # Run integrity checks
    try:
        # Check 1: Orphaned MealFood records
        orphaned_meal_foods = db.session.query(MealFood).filter(
            ~db.session.query(Meal).filter(Meal.id == MealFood.meal_id).exists()
        ).count()
        if orphaned_meal_foods > 0:
            issues.append({
                'type': 'Orphaned Meal-Food Links',
                'count': orphaned_meal_foods,
                'description': 'MealFood records with no parent Meal',
                'severity': 'warning'
            })

        # Check 2: Orphaned RecipeIngredient records
        orphaned_recipe_ingredients = db.session.query(RecipeIngredient).filter(
            ~db.session.query(Recipe).filter(Recipe.id == RecipeIngredient.recipe_id).exists()
        ).count()
        if orphaned_recipe_ingredients > 0:
            issues.append({
                'type': 'Orphaned Recipe Ingredients',
                'count': orphaned_recipe_ingredients,
                'description': 'RecipeIngredient records with no parent Recipe',
                'severity': 'warning'
            })

        # Check 3: Orphaned SavedMealItem records
        orphaned_saved_meal_items = db.session.query(SavedMealItem).filter(
            ~db.session.query(SavedMeal).filter(SavedMeal.id == SavedMealItem.saved_meal_id).exists()
        ).count()
        if orphaned_saved_meal_items > 0:
            issues.append({
                'type': 'Orphaned Saved Meal Items',
                'count': orphaned_saved_meal_items,
                'description': 'SavedMealItem records with no parent SavedMeal',
                'severity': 'warning'
            })

        # Check 4: DiaryEntry with no related content
        orphaned_entries_count = 0
        all_entries = DiaryEntry.query.all()
        for entry in all_entries:
            has_content = (
                entry.meals or
                entry.symptoms or
                entry.bowel_movements or
                entry.stress_levels or
                entry.notes
            )
            if not has_content:
                orphaned_entries_count += 1

        if orphaned_entries_count > 0:
            issues.append({
                'type': 'Empty Diary Entries',
                'count': orphaned_entries_count,
                'description': 'DiaryEntry records with no related content',
                'severity': 'info'
            })

        # Check 5: MealFood pointing to deleted Food
        invalid_meal_foods = db.session.query(MealFood).filter(
            ~db.session.query(Food).filter(Food.id == MealFood.food_id).exists()
        ).count()
        if invalid_meal_foods > 0:
            issues.append({
                'type': 'Invalid Meal-Food References',
                'count': invalid_meal_foods,
                'description': 'MealFood records pointing to deleted Food items',
                'severity': 'danger'
            })

        # Check 6: RecipeIngredient pointing to deleted Food
        invalid_recipe_ingredients = db.session.query(RecipeIngredient).filter(
            ~db.session.query(Food).filter(Food.id == RecipeIngredient.food_id).exists()
        ).count()
        if invalid_recipe_ingredients > 0:
            issues.append({
                'type': 'Invalid Recipe Ingredient References',
                'count': invalid_recipe_ingredients,
                'description': 'RecipeIngredient records pointing to deleted Food items',
                'severity': 'danger'
            })

        # Check 7: SavedMealItem pointing to deleted Food
        invalid_saved_meal_items = db.session.query(SavedMealItem).filter(
            ~db.session.query(Food).filter(Food.id == SavedMealItem.food_id).exists()
        ).count()
        if invalid_saved_meal_items > 0:
            issues.append({
                'type': 'Invalid Saved Meal Item References',
                'count': invalid_saved_meal_items,
                'description': 'SavedMealItem records pointing to deleted Food items',
                'severity': 'danger'
            })

        # Check 8: Orphaned photo files (check uploads folder)
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

    except Exception as e:
        flash(f'Error running integrity check: {str(e)}', 'error')

    return render_template('settings/integrity_check.html', issues=issues)

@bp.route('/backup-database')
def backup_database():
    """Download a backup of the database"""
    try:
        # Use Flask's instance_path for correct absolute path
        db_path = os.path.join(current_app.instance_path, 'gut_health.db')

        if not os.path.exists(db_path):
            flash('Database file not found', 'error')
            return redirect(url_for('settings.index'))

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
        flash(f'Error creating backup: {str(e)}', 'error')
        return redirect(url_for('settings.index'))

# Helper functions for help documents
def parse_markdown(md_content):
    """Convert markdown to HTML"""
    try:
        import markdown2
        return markdown2.markdown(md_content, extras=['tables', 'fenced-code-blocks', 'header-ids', 'task-list'])
    except ImportError:
        try:
            import markdown
            return markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'toc', 'nl2br'])
        except ImportError:
            import html
            return html.escape(md_content).replace('\n', '<br>')

def extract_title_from_markdown(md_content):
    """Extract title from first H1 in markdown"""
    lines = md_content.split('\n')
    for line in lines:
        if line.strip().startswith('# '):
            return line.strip()[2:].strip()
        if line.strip() and len(lines) > lines.index(line) + 1:
            next_line = lines[lines.index(line) + 1]
            if next_line.strip().startswith('==='):
                return line.strip()
    return "Untitled Document"

def get_temp_upload_dir():
    """Get or create temporary upload directory"""
    temp_dir = os.path.join(tempfile.gettempdir(), 'gut_health_help_uploads')
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

def save_upload_data(data, upload_id):
    """Save upload data to temporary file"""
    temp_dir = get_temp_upload_dir()
    file_path = os.path.join(temp_dir, f"{upload_id}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    return file_path

def load_upload_data(upload_id):
    """Load upload data from temporary file"""
    temp_dir = get_temp_upload_dir()
    file_path = os.path.join(temp_dir, f"{upload_id}.json")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def delete_upload_data(upload_id):
    """Delete temporary upload data file"""
    temp_dir = get_temp_upload_dir()
    file_path = os.path.join(temp_dir, f"{upload_id}.json")
    if os.path.exists(file_path):
        os.remove(file_path)

def get_help_docs_dir():
    """Get or create help documents directory"""
    base_dir = current_app.root_path
    help_dir = os.path.join(base_dir, 'data', 'help_docs')
    os.makedirs(help_dir, exist_ok=True)
    return help_dir

def get_help_index_path():
    """Get help documents index file path"""
    return os.path.join(get_help_docs_dir(), 'index.json')

def load_help_index():
    """Load help documents index"""
    index_path = get_help_index_path()
    if not os.path.exists(index_path):
        return []
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []

def save_help_index(documents):
    """Persist help documents index"""
    index_path = get_help_index_path()
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)

def slugify(text):
    """Simple slug for filenames"""
    text = text or ''
    slug = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    return slug or 'help-document'

def resolve_unique_filename(title, original_filename):
    """Generate a unique markdown filename"""
    base_name = secure_filename(original_filename or '')
    if not base_name:
        base_name = f"{slugify(title)}.md"
    if not base_name.lower().endswith('.md'):
        base_name = f"{base_name}.md"

    help_dir = get_help_docs_dir()
    candidate = base_name
    stem, ext = os.path.splitext(base_name)
    counter = 1
    while os.path.exists(os.path.join(help_dir, candidate)):
        candidate = f"{stem}-{counter}{ext}"
        counter += 1
    return candidate

def split_front_matter(md_content):
    """Strip YAML front matter if present"""
    if not md_content or not md_content.startswith('---'):
        return {}, md_content

    lines = md_content.splitlines()
    if len(lines) < 3:
        return {}, md_content

    end_index = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_index = i
            break

    if end_index is None:
        return {}, md_content

    meta_lines = lines[1:end_index]
    body_lines = lines[end_index + 1:]
    metadata = {}
    for line in meta_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()
    return metadata, '\n'.join(body_lines).lstrip()

def load_help_document(doc_id):
    """Load a help document entry and markdown content"""
    documents = load_help_index()
    entry = next((doc for doc in documents if doc.get('id') == doc_id), None)
    if not entry:
        return None

    doc_path = os.path.join(get_help_docs_dir(), entry.get('filename', ''))
    if not os.path.exists(doc_path):
        return None

    with open(doc_path, 'r', encoding='utf-8') as f:
        markdown_source = f.read()

    meta, body = split_front_matter(markdown_source)
    html_content = parse_markdown(body)
    return {
        **entry,
        'title': entry.get('title') or meta.get('title', entry.get('title')),
        'category': entry.get('category') or meta.get('category', entry.get('category')),
        'markdown_source': body,
        'content': html_content
    }

def format_doc_date(doc):
    """Format date for display"""
    for key in ('updated_at', 'created_at'):
        value = doc.get(key)
        if value:
            try:
                return datetime.fromisoformat(value).strftime('%b %d, %Y')
            except ValueError:
                pass
    filename = doc.get('filename')
    if filename:
        doc_path = os.path.join(get_help_docs_dir(), filename)
        if os.path.exists(doc_path):
            dt = datetime.fromtimestamp(os.path.getmtime(doc_path))
            return dt.strftime('%b %d, %Y')
    return ''

def load_help_documents(search=None, category=None):
    """Load help documents, optionally filtered"""
    documents = load_help_index()
    results = []
    search_term = (search or '').strip().lower()

    for entry in documents:
        if category and entry.get('category', '').lower() != category.lower():
            continue

        doc_path = os.path.join(get_help_docs_dir(), entry.get('filename', ''))
        if not os.path.exists(doc_path):
            continue

        with open(doc_path, 'r', encoding='utf-8') as f:
            markdown_source = f.read()

        meta, body = split_front_matter(markdown_source)

        if search_term:
            haystack = ' '.join([
                entry.get('title', ''),
                entry.get('category', ''),
                body
            ]).lower()
            if search_term not in haystack:
                continue

        html_content = parse_markdown(body)
        results.append({
            **entry,
            'title': entry.get('title') or meta.get('title', entry.get('title')),
            'category': entry.get('category') or meta.get('category', entry.get('category')),
            'content': html_content,
            'display_date': format_doc_date(entry)
        })

    results.sort(key=lambda d: (d.get('category', ''), d.get('order_index', 0), d.get('title', '')))
    return results

# Help document routes
@bp.route('/help')
def help_index():
    """Help documents list page"""
    category = request.args.get('category')
    search = request.args.get('search')

    documents = load_help_documents(search=search, category=category)

    categories = sorted({
        doc.get('category') for doc in load_help_index() if doc.get('category')
    })

    return render_template('settings/help.html', documents=documents, categories=categories, current_category=category)

@bp.route('/help/<string:doc_id>')
def help_view(doc_id):
    """View individual help document"""
    document = load_help_document(doc_id)
    if not document:
        flash('Help document not found.', 'error')
        return redirect(url_for('settings.help_index'))
    return render_template('settings/help_view.html', document=document)

@bp.route('/help/upload', methods=['POST'])
def help_upload():
    """Upload markdown file for help document"""
    import uuid

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.endswith('.md'):
        return jsonify({'error': 'Only .md files are supported'}), 400

    try:
        md_content = file.read().decode('utf-8')
        title = extract_title_from_markdown(md_content)
        upload_id = str(uuid.uuid4())

        upload_data = {
            'markdown_source': md_content,
            'filename': secure_filename(file.filename),
            'extracted_title': title,
            'category': request.form.get('category', 'General')
        }

        save_upload_data(upload_data, upload_id)

        return jsonify({'success': True, 'redirect': url_for('settings.help_preview', upload_id=upload_id)})

    except Exception as e:
        return jsonify({'error': f'{str(e)}'}), 500

@bp.route('/help/preview', methods=['GET', 'POST'])
def help_preview():
    """Preview uploaded help document before saving"""
    if request.method == 'GET':
        upload_id = request.args.get('upload_id')

        if not upload_id:
            flash('No upload ID provided. Please upload a file first.', 'error')
            return redirect(url_for('settings.help_index'))

        preview_data = load_upload_data(upload_id)

        if not preview_data:
            flash('No upload data found. Please upload a file first.', 'error')
            return redirect(url_for('settings.help_index'))

        html_preview = parse_markdown(preview_data['markdown_source'])
        preview_data['html_preview'] = html_preview

        existing_docs = load_help_index()
        existing_docs.sort(key=lambda d: (d.get('category', ''), d.get('order_index', 0), d.get('title', '')))
        categories = sorted({doc.get('category') for doc in existing_docs if doc.get('category')})

        return render_template('settings/help_preview.html', data=preview_data, existing_docs=existing_docs, categories=categories, upload_id=upload_id)

    elif request.method == 'POST':
        upload_id = request.form.get('upload_id')

        if not upload_id:
            flash('No upload ID provided. Please upload a file first.', 'error')
            return redirect(url_for('settings.help_index'))

        preview_data = load_upload_data(upload_id)

        if not preview_data:
            flash('No upload data found. Please upload a file first.', 'error')
            return redirect(url_for('settings.help_index'))

        try:
            title = request.form.get('title')
            category = request.form.get('category')
            markdown_source = request.form.get('markdown_source')

            documents = load_help_index()
            category_orders = [doc.get('order_index', 0) for doc in documents if doc.get('category') == category]
            max_order = max(category_orders, default=0)

            filename = resolve_unique_filename(title, preview_data.get('filename'))
            doc_id = str(uuid.uuid4())
            now_iso = datetime.utcnow().isoformat()

            doc_path = os.path.join(get_help_docs_dir(), filename)
            with open(doc_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(markdown_source or '')

            documents.append({
                'id': doc_id,
                'category': category,
                'title': title,
                'filename': filename,
                'order_index': max_order + 1,
                'created_at': now_iso,
                'updated_at': now_iso
            })
            save_help_index(documents)

            delete_upload_data(upload_id)

            flash(f'Help document "{title}" added successfully!', 'success')
            return redirect(url_for('settings.help_index'))

        except Exception as e:
            flash(f'Error saving document: {str(e)}', 'error')
            return redirect(url_for('settings.help_preview', upload_id=upload_id))

@bp.route('/help/edit/<string:doc_id>', methods=['GET', 'POST'])
def help_edit(doc_id):
    """Edit help document"""
    document = load_help_document(doc_id)
    if not document:
        flash('Help document not found.', 'error')
        return redirect(url_for('settings.help_index'))

    if request.method == 'POST':
        try:
            md_content = request.form.get('markdown_source')
            custom_title = request.form.get('title')
            category = request.form.get('category')

            document['markdown_source'] = md_content
            document['content'] = parse_markdown(md_content)
            document['title'] = custom_title if custom_title else extract_title_from_markdown(md_content)
            document['category'] = category

            documents = load_help_index()
            for entry in documents:
                if entry.get('id') == doc_id:
                    previous_category = entry.get('category')
                    entry['title'] = document['title']
                    entry['category'] = category
                    if previous_category != category:
                        category_orders = [doc.get('order_index', 0) for doc in documents if doc.get('category') == category]
                        entry['order_index'] = max(category_orders, default=0) + 1
                    entry['updated_at'] = datetime.utcnow().isoformat()
                    break

            doc_path = os.path.join(get_help_docs_dir(), document.get('filename', ''))
            with open(doc_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(md_content or '')

            save_help_index(documents)
            flash('Help document updated successfully!', 'success')
            return redirect(url_for('settings.help_index'))

        except Exception as e:
            flash(f'Error updating document: {str(e)}', 'error')

    existing_docs = [doc for doc in load_help_index() if doc.get('id') != doc_id]
    existing_docs.sort(key=lambda d: (d.get('category', ''), d.get('order_index', 0), d.get('title', '')))
    categories = sorted({doc.get('category') for doc in load_help_index() if doc.get('category')})

    return render_template('settings/help_edit.html', document=document, existing_docs=existing_docs, categories=categories)

@bp.route('/help/delete/<string:doc_id>', methods=['POST'])
def help_delete(doc_id):
    """Delete a help document"""
    try:
        documents = load_help_index()
        document = next((doc for doc in documents if doc.get('id') == doc_id), None)
        if not document:
            return jsonify({'error': 'Document not found'}), 404

        doc_path = os.path.join(get_help_docs_dir(), document.get('filename', ''))
        if os.path.exists(doc_path):
            os.remove(doc_path)

        documents = [doc for doc in documents if doc.get('id') != doc_id]
        save_help_index(documents)

        flash('Help document deleted successfully!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/help/preview_markdown', methods=['POST'])
def help_preview_markdown():
    """Convert markdown to HTML for live preview"""
    try:
        md_content = request.json.get('markdown', '')
        html_content = parse_markdown(md_content)
        return jsonify({'html': html_content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
