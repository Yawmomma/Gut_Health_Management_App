from flask import Blueprint, render_template, send_file, flash, redirect, url_for, request, jsonify, current_app
import os
import shutil
import json
import tempfile
from datetime import datetime
from werkzeug.utils import secure_filename
from database import db
from models.diary import DiaryEntry, Meal, MealFood, Symptom, BowelMovement, StressLog, Note
from models.food import Food
from models.recipe import Recipe, RecipeIngredient, SavedMeal, SavedMealItem
from models.education import HelpDocument

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

# Help document routes
@bp.route('/help')
def help_index():
    """Help documents list page"""
    category = request.args.get('category')
    search = request.args.get('search')

    query = HelpDocument.query

    if search:
        search_filter = f'%{search}%'
        query = query.filter(
            (HelpDocument.title.ilike(search_filter)) |
            (HelpDocument.category.ilike(search_filter)) |
            (HelpDocument.content.ilike(search_filter))
        )
    elif category:
        query = query.filter(HelpDocument.category.ilike(f'%{category}%'))

    documents = query.order_by(HelpDocument.category, HelpDocument.order_index).all()

    # Get unique categories for filtering
    categories = db.session.query(HelpDocument.category).distinct().all()
    categories = sorted([cat[0] for cat in categories if cat[0]])

    return render_template('settings/help.html', documents=documents, categories=categories, current_category=category)

@bp.route('/help/<int:doc_id>')
def help_view(doc_id):
    """View individual help document"""
    document = HelpDocument.query.get_or_404(doc_id)
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

        existing_docs = HelpDocument.query.order_by(HelpDocument.category, HelpDocument.order_index).all()
        categories = db.session.query(HelpDocument.category).distinct().all()
        categories = sorted([cat[0] for cat in categories if cat[0]])

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

            html_content = parse_markdown(markdown_source)

            # Get next order index for this category
            max_order = db.session.query(db.func.max(HelpDocument.order_index)).filter_by(category=category).scalar() or 0

            document = HelpDocument(
                category=category,
                title=title,
                content=html_content,
                markdown_source=markdown_source,
                filename=preview_data['filename'],
                is_markdown=True,
                order_index=max_order + 1
            )

            db.session.add(document)
            db.session.commit()

            delete_upload_data(upload_id)

            flash(f'Help document "{title}" added successfully!', 'success')
            return redirect(url_for('settings.help_index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error saving document: {str(e)}', 'error')
            return redirect(url_for('settings.help_preview', upload_id=upload_id))

@bp.route('/help/edit/<int:doc_id>', methods=['GET', 'POST'])
def help_edit(doc_id):
    """Edit help document"""
    document = HelpDocument.query.get_or_404(doc_id)

    if request.method == 'POST':
        try:
            md_content = request.form.get('markdown_source')
            custom_title = request.form.get('title')
            category = request.form.get('category')

            document.markdown_source = md_content
            document.content = parse_markdown(md_content)
            document.title = custom_title if custom_title else extract_title_from_markdown(md_content)
            document.category = category

            db.session.commit()
            flash('Help document updated successfully!', 'success')
            return redirect(url_for('settings.help_view', doc_id=doc_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating document: {str(e)}', 'error')

    existing_docs = HelpDocument.query.filter(HelpDocument.id != doc_id).order_by(HelpDocument.category, HelpDocument.order_index).all()
    categories = db.session.query(HelpDocument.category).distinct().all()
    categories = sorted([cat[0] for cat in categories if cat[0]])

    return render_template('settings/help_edit.html', document=document, existing_docs=existing_docs, categories=categories)

@bp.route('/help/delete/<int:doc_id>', methods=['POST'])
def help_delete(doc_id):
    """Delete a help document"""
    try:
        document = HelpDocument.query.get_or_404(doc_id)
        db.session.delete(document)
        db.session.commit()
        flash('Help document deleted successfully!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
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
