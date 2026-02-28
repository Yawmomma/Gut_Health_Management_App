from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from database import db
from models.recipe import Recipe, RecipeIngredient, SavedMeal, SavedMealItem, RecipeClassificationOption
from models.food import Food
from utils import allowed_file
import recipe_categories as rc
from werkzeug.utils import secure_filename
import os
from sqlalchemy import func

bp = Blueprint('recipes', __name__, url_prefix='/recipes')

def save_upload_file(file, prefix='recipe'):
    """Save uploaded file and return the path"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to avoid filename conflicts
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        filename = f"{prefix}_{timestamp}_{name}{ext}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return f"uploads/{filename}"
    return None

def get_classification_options(option_type, base_list, include_value=None):
    """Merge base list with custom options, preserving display order."""
    custom_values = RecipeClassificationOption.query.filter_by(option_type=option_type).order_by(
        RecipeClassificationOption.value.asc()
    ).all()
    combined = list(base_list)
    seen = {value.lower() for value in combined}
    for option in custom_values:
        if option.value.lower() not in seen:
            combined.append(option.value)
            seen.add(option.value.lower())
    if include_value and include_value.lower() not in seen:
        combined.append(include_value)
    return combined

def resolve_custom_option(option_type, selected_value, custom_value, base_list):
    """Resolve custom selections and persist new options for future use."""
    if selected_value == '__custom__':
        custom_value = (custom_value or '').strip()
        if not custom_value:
            return None
        base_lower = {value.lower() for value in base_list}
        if custom_value.lower() not in base_lower:
            existing = RecipeClassificationOption.query.filter(
                RecipeClassificationOption.option_type == option_type,
                func.lower(RecipeClassificationOption.value) == custom_value.lower()
            ).first()
            if not existing:
                db.session.add(RecipeClassificationOption(option_type=option_type, value=custom_value))
        return custom_value
    return selected_value

def safe_delete_file(filepath):
    """Safely delete a file, logging errors but not failing the operation."""
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            return True
    except OSError as e:
        current_app.logger.warning(f'Could not delete file {filepath}: {e}')
    return False

def process_recipe_classification(form, removed_tags):
    """Process recipe classification fields from form, filtering removed tags."""
    def filter_tag(value):
        """Return None if value is in removed_tags, else return value."""
        return None if (value and value.strip() in removed_tags) else value

    subcategory = filter_tag(form.get('subcategory'))

    cuisine = resolve_custom_option(
        'cuisine', form.get('cuisine'), form.get('custom_cuisine'), rc.CUISINES
    )
    cuisine = filter_tag(cuisine)

    preparation_method = resolve_custom_option(
        'preparation_method', form.get('preparation_methods'),
        form.get('custom_preparation_method'), rc.PREPARATION_METHODS
    )
    preparation_method = filter_tag(preparation_method)

    occasion = resolve_custom_option(
        'occasion', form.get('occasions'), form.get('custom_occasion'), rc.OCCASIONS
    )
    occasion = filter_tag(occasion)

    difficulty = filter_tag(form.get('difficulty'))

    return {
        'subcategory': subcategory,
        'cuisine': cuisine,
        'preparation_method': preparation_method,
        'occasion': occasion,
        'difficulty': difficulty
    }

@bp.route('/')
def index():
    """My Recipe Book landing page"""
    recipe_count = Recipe.query.count()
    meal_count = SavedMeal.query.count()
    return render_template('recipes/index.html', recipe_count=recipe_count, meal_count=meal_count)

@bp.route('/chat')
def chat():
    """Recipe helper chat interface"""
    return render_template('recipes/chat.html')

@bp.route('/saved')
def saved():
    """Saved recipes list - Placeholder for Phase 6 (LLM integration)"""
    flash('Saved recipes feature coming soon!', 'info')
    return redirect(url_for('recipes.index'))

@bp.route('/saved/<int:recipe_id>')
def detail(recipe_id):
    """Recipe detail view - Placeholder for Phase 6 (LLM integration)"""
    flash('Saved recipes feature coming soon!', 'info')
    return redirect(url_for('recipes.index'))


# User-created recipes with food library
@bp.route('/my-recipes')
def my_recipes():
    """List all user-created recipes"""
    recipes = Recipe.query.order_by(Recipe.created_at.desc()).all()
    return render_template('recipes/my_recipes.html', recipes=recipes, meal_types=rc.MEAL_TYPES)


@bp.route('/my-recipes/category/<category>')
def recipe_category(category):
    """View recipes in a specific category"""
    if category == 'Uncategorized':
        recipes = Recipe.query.filter_by(category=None).order_by(Recipe.created_at.desc()).all()
    else:
        recipes = Recipe.query.filter_by(category=category).order_by(Recipe.created_at.desc()).all()
    return render_template('recipes/recipe_category.html', recipes=recipes, category=category)


@bp.route('/my-recipes/create', methods=['GET', 'POST'])
def create_recipe():
    """Create a new recipe"""
    if request.method == 'POST':
        try:
            # Get dietary needs as comma-separated list (can select multiple)
            dietary_needs_list = request.form.getlist('dietary_needs')
            dietary_needs_str = ', '.join(dietary_needs_list) if dietary_needs_list else None

            # Get removed tags
            removed_tags_str = request.form.get('removed_tags', '')
            removed_tags = set(tag.strip() for tag in removed_tags_str.split(',') if tag.strip())

            # Filter dietary needs to exclude removed tags
            if removed_tags:
                dietary_needs_list = [need for need in dietary_needs_list if need.strip() not in removed_tags]
                dietary_needs_str = ', '.join(dietary_needs_list) if dietary_needs_list else None

            # Handle photo upload
            image_path = None
            if 'recipe_photo' in request.files:
                file = request.files['recipe_photo']
                if file.filename:
                    image_path = save_upload_file(file, prefix='recipe')

            # Process classification fields (filter removed tags)
            classification = process_recipe_classification(request.form, removed_tags)

            # Create recipe
            recipe = Recipe(
                name=request.form.get('name'),
                description=request.form.get('description'),
                servings=int(request.form.get('servings', 1)),
                prep_time=request.form.get('prep_time'),
                cook_time=request.form.get('cook_time'),
                instructions=request.form.get('instructions'),
                notes=request.form.get('notes'),
                category=request.form.get('category'),
                subcategory=classification['subcategory'],
                cuisine=classification['cuisine'],
                dietary_needs=dietary_needs_str,
                preparation_method=classification['preparation_method'],
                occasion=classification['occasion'],
                difficulty=classification['difficulty'],
                tags=request.form.get('tags'),
                source_url=request.form.get('source_url'),
                image_path=image_path
            )
            db.session.add(recipe)
            db.session.flush()

            # Add ingredients
            food_ids = request.form.getlist('food_ids[]')
            quantities = request.form.getlist('quantities[]')
            ingredient_notes = request.form.getlist('ingredient_notes[]')

            for i, food_id in enumerate(food_ids):
                if food_id:
                    ingredient = RecipeIngredient(
                        recipe_id=recipe.id,
                        food_id=int(food_id),
                        quantity=quantities[i] if i < len(quantities) else '',
                        notes=ingredient_notes[i] if i < len(ingredient_notes) else ''
                    )
                    db.session.add(ingredient)

            db.session.commit()
            flash(f'Recipe "{recipe.name}" added successfully!', 'success')
            return redirect(url_for('recipes.view_recipe', recipe_id=recipe.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating recipe: {str(e)}', 'error')

    # GET request - show form
    foods = Food.query.order_by(Food.category, Food.name).all()
    foods_data = [f.to_recipe_dict() for f in foods]

    cuisines = get_classification_options('cuisine', rc.CUISINES)
    preparation_methods = get_classification_options('preparation_method', rc.PREPARATION_METHODS)
    occasions = get_classification_options('occasion', rc.OCCASIONS)

    return render_template('recipes/create_recipe.html',
                         foods=foods_data,
                         meal_types=rc.MEAL_TYPES,
                         all_subcategories=rc.ALL_SUBCATEGORIES,
                         cuisines=cuisines,
                         dietary_needs=rc.DIETARY_NEEDS,
                         preparation_methods=preparation_methods,
                         occasions=occasions,
                         difficulty_levels=rc.DIFFICULTY_LEVELS)


@bp.route('/my-recipes/<int:recipe_id>')
def view_recipe(recipe_id):
    """View recipe detail"""
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template('recipes/view_recipe.html', recipe=recipe)


@bp.route('/my-recipes/<int:recipe_id>/edit', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    """Edit a recipe"""
    recipe = Recipe.query.get_or_404(recipe_id)

    if request.method == 'POST':
        try:
            # Get dietary needs as comma-separated list
            dietary_needs_list = request.form.getlist('dietary_needs')
            dietary_needs_str = ', '.join(dietary_needs_list) if dietary_needs_list else None

            # Get removed tags
            removed_tags_str = request.form.get('removed_tags', '')
            removed_tags = set(tag.strip() for tag in removed_tags_str.split(',') if tag.strip())

            # Filter dietary needs to exclude removed tags
            if removed_tags:
                dietary_needs_list = [need for need in dietary_needs_list if need.strip() not in removed_tags]
                dietary_needs_str = ', '.join(dietary_needs_list) if dietary_needs_list else None

            # Handle photo upload
            if 'recipe_photo' in request.files:
                file = request.files['recipe_photo']
                if file.filename:
                    # Delete old photo if exists
                    if recipe.image_path:
                        old_path = os.path.join(current_app.root_path, 'static', recipe.image_path)
                        safe_delete_file(old_path)
                    # Save new photo
                    recipe.image_path = save_upload_file(file, prefix='recipe')

            # Process classification fields (filter removed tags)
            classification = process_recipe_classification(request.form, removed_tags)

            # Update recipe
            recipe.name = request.form.get('name')
            recipe.description = request.form.get('description')
            recipe.servings = int(request.form.get('servings', 1))
            recipe.prep_time = request.form.get('prep_time')
            recipe.cook_time = request.form.get('cook_time')
            recipe.instructions = request.form.get('instructions')
            recipe.notes = request.form.get('notes')
            recipe.category = request.form.get('category')
            recipe.subcategory = classification['subcategory']
            recipe.cuisine = classification['cuisine']
            recipe.dietary_needs = dietary_needs_str
            recipe.preparation_method = classification['preparation_method']
            recipe.occasion = classification['occasion']
            recipe.difficulty = classification['difficulty']
            recipe.tags = request.form.get('tags')
            recipe.source_url = request.form.get('source_url')

            # Delete existing ingredients
            RecipeIngredient.query.filter_by(recipe_id=recipe.id).delete()

            # Add new ingredients
            food_ids = request.form.getlist('food_ids[]')
            quantities = request.form.getlist('quantities[]')
            ingredient_notes = request.form.getlist('ingredient_notes[]')

            for i, food_id in enumerate(food_ids):
                if food_id:
                    ingredient = RecipeIngredient(
                        recipe_id=recipe.id,
                        food_id=int(food_id),
                        quantity=quantities[i] if i < len(quantities) else '',
                        notes=ingredient_notes[i] if i < len(ingredient_notes) else ''
                    )
                    db.session.add(ingredient)

            db.session.commit()
            flash(f'Recipe "{recipe.name}" updated successfully!', 'success')
            return redirect(url_for('recipes.view_recipe', recipe_id=recipe.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating recipe: {str(e)}', 'error')

    foods = Food.query.order_by(Food.category, Food.name).all()
    foods_data = [f.to_recipe_dict() for f in foods]

    # Convert recipe ingredients to dictionaries for JSON serialization
    ingredients_data = [{
        'id': ing.id,
        'food_id': ing.food_id,
        'quantity': ing.quantity,
        'notes': ing.notes or '',
        'food': {
            'id': ing.food.id,
            'name': ing.food.name,
            'category': ing.food.category,
            'fructans': ing.food.fructans,
            'gos': ing.food.gos,
            'lactose': ing.food.lactose,
            'fructose': ing.food.fructose,
            'polyols': ing.food.polyols,
            'histamine_level': ing.food.histamine_level
        }
    } for ing in recipe.ingredients]

    prep_include = recipe.preparation_method.split(',')[0].strip() if recipe.preparation_method else None
    occasion_include = recipe.occasion.split(',')[0].strip() if recipe.occasion else None

    cuisines = get_classification_options('cuisine', rc.CUISINES, include_value=recipe.cuisine)
    preparation_methods = get_classification_options('preparation_method', rc.PREPARATION_METHODS, include_value=prep_include)
    occasions = get_classification_options('occasion', rc.OCCASIONS, include_value=occasion_include)

    return render_template('recipes/edit_recipe.html',
                         recipe=recipe,
                         foods=foods_data,
                         ingredients=ingredients_data,
                         meal_types=rc.MEAL_TYPES,
                         all_subcategories=rc.ALL_SUBCATEGORIES,
                         cuisines=cuisines,
                         dietary_needs=rc.DIETARY_NEEDS,
                         preparation_methods=preparation_methods,
                         occasions=occasions,
                         difficulty_levels=rc.DIFFICULTY_LEVELS)


@bp.route('/my-recipes/<int:recipe_id>/delete', methods=['POST'])
def delete_recipe(recipe_id):
    """Delete a recipe"""
    recipe = Recipe.query.get_or_404(recipe_id)
    try:
        db.session.delete(recipe)
        db.session.commit()
        flash(f'Recipe "{recipe.name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting recipe: {str(e)}', 'error')
    return redirect(url_for('recipes.my_recipes'))


# Saved Meals
@bp.route('/my-meals')
def my_meals():
    """List all saved meals"""
    meals = SavedMeal.query.order_by(SavedMeal.created_at.desc()).all()
    return render_template('recipes/my_meals.html', meals=meals)


@bp.route('/my-meals/create', methods=['GET', 'POST'])
def create_meal():
    """Create a new saved meal"""
    if request.method == 'POST':
        try:
            # Handle photo upload
            image_path = None
            if 'meal_photo' in request.files:
                file = request.files['meal_photo']
                if file.filename:
                    image_path = save_upload_file(file, prefix='meal')

            # Create saved meal
            meal = SavedMeal(
                name=request.form.get('name'),
                description=request.form.get('description'),
                meal_type=request.form.get('meal_type'),
                image_path=image_path
            )
            db.session.add(meal)
            db.session.flush()

            # Add meal items
            food_ids = request.form.getlist('food_ids[]')
            portions = request.form.getlist('portions[]')

            for i, food_id in enumerate(food_ids):
                if food_id:
                    item = SavedMealItem(
                        saved_meal_id=meal.id,
                        food_id=int(food_id),
                        portion_size=portions[i] if i < len(portions) else ''
                    )
                    db.session.add(item)

            db.session.commit()
            flash(f'Meal "{meal.name}" added successfully!', 'success')
            return redirect(url_for('recipes.my_meals'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating meal: {str(e)}', 'error')

    # GET request - show form
    foods = Food.query.order_by(Food.category, Food.name).all()
    foods_data = [f.to_recipe_dict() for f in foods]
    return render_template('recipes/create_meal.html', foods=foods_data)


@bp.route('/my-meals/<int:meal_id>/edit', methods=['GET', 'POST'])
def edit_meal(meal_id):
    """Edit a saved meal"""
    meal = SavedMeal.query.get_or_404(meal_id)

    if request.method == 'POST':
        try:
            # Update meal details
            meal.name = request.form.get('name')
            meal.description = request.form.get('description')
            meal.meal_type = request.form.get('meal_type')

            # Handle photo upload
            if 'meal_photo' in request.files:
                file = request.files['meal_photo']
                if file.filename:
                    # Delete old photo if exists
                    if meal.image_path:
                        old_path = os.path.join('static', meal.image_path.lstrip('/'))
                        safe_delete_file(old_path)
                    # Save new photo
                    meal.image_path = save_upload_file(file, prefix='meal')

            # Replace meal items (delete old, add new)
            SavedMealItem.query.filter_by(saved_meal_id=meal.id).delete()

            food_ids = request.form.getlist('food_ids[]')
            portions = request.form.getlist('portions[]')

            for i, food_id in enumerate(food_ids):
                if food_id:
                    item = SavedMealItem(
                        saved_meal_id=meal.id,
                        food_id=int(food_id),
                        portion_size=portions[i] if i < len(portions) else ''
                    )
                    db.session.add(item)

            db.session.commit()
            flash(f'Meal "{meal.name}" updated successfully!', 'success')
            return redirect(url_for('recipes.my_meals'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating meal: {str(e)}', 'error')

    # GET request - load meal data
    foods = Food.query.order_by(Food.category, Food.name).all()
    foods_data = [{
        'id': f.id,
        'name': f.name,
        'category': f.category,
        'fructans': f.fructans,
        'gos': f.gos,
        'lactose': f.lactose,
        'fructose': f.fructose,
        'polyols': f.polyols,
        'mannitol': f.mannitol,
        'sorbitol': f.sorbitol,
        'histamine_level': f.histamine_level,
        'safe_serving': f.safe_serving
    } for f in foods]

    # Convert existing meal items to dict
    meal_items_data = [{
        'food_id': item.food_id,
        'portion_size': item.portion_size,
        'food': {
            'id': item.food.id,
            'name': item.food.name,
            'category': item.food.category
        }
    } for item in meal.meal_items]

    return render_template('recipes/edit_meal.html',
                         meal=meal,
                         foods=foods_data,
                         meal_items=meal_items_data)


@bp.route('/my-meals/<int:meal_id>/delete', methods=['POST'])
def delete_meal(meal_id):
    """Delete a saved meal"""
    meal = SavedMeal.query.get_or_404(meal_id)
    try:
        # Delete photo if exists
        if meal.image_path:
            photo_path = os.path.join('static', meal.image_path.lstrip('/'))
            safe_delete_file(photo_path)

        db.session.delete(meal)
        db.session.commit()
        flash(f'Meal "{meal.name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting meal: {str(e)}', 'error')
    return redirect(url_for('recipes.my_meals'))
