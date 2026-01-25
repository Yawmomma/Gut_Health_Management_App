from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from database import db
from models.user import SavedRecipe
from models.recipe import Recipe, RecipeIngredient, SavedMeal, SavedMealItem
from models.food import Food
import recipe_categories as rc
from werkzeug.utils import secure_filename
import os

bp = Blueprint('recipes', __name__, url_prefix='/recipes')

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

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

@bp.route('/')
def index():
    """Recipes & Meals landing page"""
    recipe_count = Recipe.query.count()
    meal_count = SavedMeal.query.count()
    return render_template('recipes/index.html', recipe_count=recipe_count, meal_count=meal_count)

@bp.route('/chat')
def chat():
    """Recipe helper chat interface"""
    return render_template('recipes/chat.html')

@bp.route('/saved')
def saved():
    """Saved recipes list"""
    recipes = SavedRecipe.query.order_by(SavedRecipe.created_at.desc()).all()
    return render_template('recipes/saved.html', recipes=recipes)

@bp.route('/saved/<int:recipe_id>')
def detail(recipe_id):
    """Recipe detail view"""
    recipe = SavedRecipe.query.get_or_404(recipe_id)
    return render_template('recipes/detail.html', recipe=recipe)


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

            # Filter out removed tags from form fields
            subcategory = request.form.get('subcategory')
            if subcategory and subcategory.strip() in removed_tags:
                subcategory = None

            cuisine = request.form.get('cuisine')
            if cuisine and cuisine.strip() in removed_tags:
                cuisine = None

            main_ingredient = request.form.get('main_ingredient')
            if main_ingredient and main_ingredient.strip() in removed_tags:
                main_ingredient = None

            preparation_method = request.form.get('preparation_method')
            if preparation_method and preparation_method.strip() in removed_tags:
                preparation_method = None

            occasion = request.form.get('occasion')
            if occasion and occasion.strip() in removed_tags:
                occasion = None

            difficulty = request.form.get('difficulty')
            if difficulty and difficulty.strip() in removed_tags:
                difficulty = None

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
                subcategory=subcategory,
                cuisine=cuisine,
                main_ingredient=main_ingredient,
                dietary_needs=dietary_needs_str,
                preparation_method=preparation_method,
                occasion=occasion,
                difficulty=difficulty,
                tags=request.form.get('tags'),
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
    # Convert foods to dictionaries for JSON serialization
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

    return render_template('recipes/create_recipe.html',
                         foods=foods_data,
                         meal_types=rc.MEAL_TYPES,
                         all_subcategories=rc.ALL_SUBCATEGORIES,
                         cuisines=rc.CUISINES,
                         main_ingredients=rc.MAIN_INGREDIENTS,
                         dietary_needs=rc.DIETARY_NEEDS,
                         preparation_methods=rc.PREPARATION_METHODS,
                         occasions=rc.OCCASIONS,
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
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    # Save new photo
                    recipe.image_path = save_upload_file(file, prefix='recipe')

            # Filter out removed tags from form fields
            subcategory = request.form.get('subcategory')
            if subcategory and subcategory.strip() in removed_tags:
                subcategory = None

            cuisine = request.form.get('cuisine')
            if cuisine and cuisine.strip() in removed_tags:
                cuisine = None

            main_ingredient = request.form.get('main_ingredient')
            if main_ingredient and main_ingredient.strip() in removed_tags:
                main_ingredient = None

            preparation_method = request.form.get('preparation_method')
            if preparation_method and preparation_method.strip() in removed_tags:
                preparation_method = None

            occasion = request.form.get('occasion')
            if occasion and occasion.strip() in removed_tags:
                occasion = None

            difficulty = request.form.get('difficulty')
            if difficulty and difficulty.strip() in removed_tags:
                difficulty = None

            # Update recipe
            recipe.name = request.form.get('name')
            recipe.description = request.form.get('description')
            recipe.servings = int(request.form.get('servings', 1))
            recipe.prep_time = request.form.get('prep_time')
            recipe.cook_time = request.form.get('cook_time')
            recipe.instructions = request.form.get('instructions')
            recipe.notes = request.form.get('notes')
            recipe.category = request.form.get('category')
            recipe.subcategory = subcategory
            recipe.cuisine = cuisine
            recipe.main_ingredient = main_ingredient
            recipe.dietary_needs = dietary_needs_str
            recipe.preparation_method = preparation_method
            recipe.occasion = occasion
            recipe.difficulty = difficulty
            recipe.tags = request.form.get('tags')

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
    # Convert foods to dictionaries for JSON serialization
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

    return render_template('recipes/edit_recipe.html',
                         recipe=recipe,
                         foods=foods_data,
                         ingredients=ingredients_data,
                         meal_types=rc.MEAL_TYPES,
                         all_subcategories=rc.ALL_SUBCATEGORIES,
                         cuisines=rc.CUISINES,
                         main_ingredients=rc.MAIN_INGREDIENTS,
                         dietary_needs=rc.DIETARY_NEEDS,
                         preparation_methods=rc.PREPARATION_METHODS,
                         occasions=rc.OCCASIONS,
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
    # Convert foods to dictionaries for JSON serialization
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
                        import os
                        old_path = os.path.join('static', meal.image_path.lstrip('/'))
                        if os.path.exists(old_path):
                            os.remove(old_path)
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
            import os
            photo_path = os.path.join('static', meal.image_path.lstrip('/'))
            if os.path.exists(photo_path):
                os.remove(photo_path)

        db.session.delete(meal)
        db.session.commit()
        flash(f'Meal "{meal.name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting meal: {str(e)}', 'error')
    return redirect(url_for('recipes.my_meals'))
