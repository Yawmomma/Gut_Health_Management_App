"""
Recipe Builder Blueprint
Browse, search, and import recipes from external dataset (2.15M recipes).
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from database import db
from models.recipe import Recipe, RecipeIngredient, SavedMeal, SavedMealItem, ArchivedExternalRecipe
from models.food import Food
from utils.recipe_search import (
    search_recipes,
    search_by_ingredients,
    get_random_recipes,
    get_recipe_by_hash,
    get_total_recipe_count,
    get_parquet_files
)
from utils.recipe_parser import (
    parse_recipe_text,
    format_ingredients_for_display,
    format_directions_for_display,
    extract_ingredient_names
)
import recipe_categories as rc

bp = Blueprint('recipe_builder', __name__, url_prefix='/recipes/builder')


@bp.route('/')
def index():
    """Recipe Builder main page - browse and search external recipes."""
    # Check if parquet files exist
    parquet_files = get_parquet_files()
    has_data = len(parquet_files) > 0
    total_recipes = get_total_recipe_count() if has_data else 0

    # Get archived count
    archived_count = ArchivedExternalRecipe.query.count()

    return render_template(
        'recipes/builder.html',
        has_data=has_data,
        total_recipes=total_recipes,
        archived_count=archived_count
    )


@bp.route('/search')
def search():
    """Search recipes by keyword or ingredients."""
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'keyword')  # 'keyword' or 'ingredients'
    page = request.args.get('page', 1, type=int)
    per_page = 20

    if not query:
        return jsonify({'recipes': [], 'total': 0, 'page': page})

    # Get archived hashes to exclude
    archived_hashes = ArchivedExternalRecipe.get_archived_hashes()

    if search_type == 'ingredients':
        # Split by comma for ingredient search
        ingredients = [i.strip() for i in query.split(',') if i.strip()]
        recipes = search_by_ingredients(
            ingredients,
            match_all=True,
            limit=per_page,
            archived_hashes=archived_hashes
        )
    else:
        recipes = search_recipes(
            query,
            limit=per_page,
            offset=(page - 1) * per_page,
            archived_hashes=archived_hashes
        )

    return jsonify({
        'recipes': recipes,
        'total': len(recipes),
        'page': page,
        'query': query
    })


@bp.route('/random')
def random_recipes():
    """Get random recipes for inspiration."""
    limit = request.args.get('limit', 10, type=int)
    archived_hashes = ArchivedExternalRecipe.get_archived_hashes()

    recipes = get_random_recipes(limit=limit, archived_hashes=archived_hashes)
    return jsonify({'recipes': recipes})


@bp.route('/preview/<recipe_hash>')
def preview(recipe_hash):
    """Preview a specific recipe before importing."""
    recipe = get_recipe_by_hash(recipe_hash)
    if not recipe:
        flash('Recipe not found', 'error')
        return redirect(url_for('recipe_builder.index'))

    # Check if archived
    is_archived = ArchivedExternalRecipe.is_archived(recipe_hash)

    # Get all foods for potential ingredient matching
    foods = Food.query.order_by(Food.name).all()
    foods_data = [{
        'id': f.id,
        'name': f.name,
        'category': f.category
    } for f in foods]

    # Try to match ingredients to food library
    ingredient_names = extract_ingredient_names(recipe['ingredients'])
    matched_foods = []
    for ing_name in ingredient_names:
        # Simple fuzzy match - find foods that contain the ingredient name
        for food in foods:
            if ing_name in food.name.lower():
                matched_foods.append({
                    'ingredient': ing_name,
                    'food_id': food.id,
                    'food_name': food.name
                })
                break

    return render_template(
        'recipes/builder_preview.html',
        recipe=recipe,
        is_archived=is_archived,
        foods=foods_data,
        matched_foods=matched_foods,
        meal_types=rc.MEAL_TYPES
    )


@bp.route('/archive/<recipe_hash>', methods=['POST'])
def archive(recipe_hash):
    """Archive a recipe (hide it from future searches)."""
    recipe_name = request.form.get('recipe_name', 'Unknown')
    ArchivedExternalRecipe.archive_recipe(recipe_hash, recipe_name)
    flash(f'Recipe "{recipe_name}" archived. It won\'t appear in future searches.', 'info')

    # Return to previous page or builder index
    return redirect(request.referrer or url_for('recipe_builder.index'))


@bp.route('/unarchive/<recipe_hash>', methods=['POST'])
def unarchive(recipe_hash):
    """Unarchive a recipe."""
    ArchivedExternalRecipe.unarchive_recipe(recipe_hash)
    flash('Recipe restored from archive.', 'success')
    return redirect(request.referrer or url_for('recipe_builder.archived'))


@bp.route('/archived')
def archived():
    """View all archived recipes."""
    archived_recipes = ArchivedExternalRecipe.query.order_by(
        ArchivedExternalRecipe.archived_at.desc()
    ).all()
    return render_template('recipes/builder_archived.html', archived_recipes=archived_recipes)


@bp.route('/save-to-recipes', methods=['POST'])
def save_to_recipes():
    """Save external recipe to user's recipe collection."""
    try:
        recipe_hash = request.form.get('recipe_hash')
        recipe_name = request.form.get('name')
        description = request.form.get('description', '')
        servings = request.form.get('servings', 1, type=int)
        category = request.form.get('category')
        instructions = request.form.get('instructions', '')

        # Create new recipe
        recipe = Recipe(
            name=recipe_name,
            description=description,
            servings=servings,
            category=category,
            instructions=instructions,
            notes=f"Imported from Recipe Builder (hash: {recipe_hash})"
        )
        db.session.add(recipe)
        db.session.flush()

        # Add any matched ingredients
        food_ids = request.form.getlist('food_ids[]')
        quantities = request.form.getlist('quantities[]')
        notes = request.form.getlist('ingredient_notes[]')

        for i, food_id in enumerate(food_ids):
            if food_id:
                ingredient = RecipeIngredient(
                    recipe_id=recipe.id,
                    food_id=int(food_id),
                    quantity=quantities[i] if i < len(quantities) else '',
                    notes=notes[i] if i < len(notes) else ''
                )
                db.session.add(ingredient)

        db.session.commit()
        flash(f'Recipe "{recipe_name}" saved to your collection!', 'success')
        return redirect(url_for('recipes.view_recipe', recipe_id=recipe.id))

    except Exception as e:
        db.session.rollback()
        flash(f'Error saving recipe: {str(e)}', 'error')
        return redirect(url_for('recipe_builder.index'))


@bp.route('/save-to-meals', methods=['POST'])
def save_to_meals():
    """Save external recipe as a saved meal."""
    try:
        recipe_hash = request.form.get('recipe_hash')
        meal_name = request.form.get('name')
        description = request.form.get('description', '')
        meal_type = request.form.get('meal_type')

        # Create new saved meal
        meal = SavedMeal(
            name=meal_name,
            description=description,
            meal_type=meal_type
        )
        db.session.add(meal)
        db.session.flush()

        # Add any matched ingredients as meal items
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
        flash(f'Meal "{meal_name}" saved to your collection!', 'success')
        return redirect(url_for('recipes.my_meals'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error saving meal: {str(e)}', 'error')
        return redirect(url_for('recipe_builder.index'))


@bp.route('/api/match-ingredients', methods=['POST'])
def match_ingredients():
    """API endpoint to match ingredient text to food library."""
    data = request.get_json()
    ingredients = data.get('ingredients', [])

    if not ingredients:
        return jsonify({'matches': []})

    try:
        matches = []
        ingredient_names = extract_ingredient_names(ingredients)

        for ing_name in ingredient_names:
            # Use database query instead of loading all foods into memory
            # This is much more efficient, especially with 317k+ USDA foods
            food = Food.query.filter(
                Food.name.ilike(f'%{ing_name}%')
            ).first()

            if food:
                matches.append({
                    'ingredient': ing_name,
                    'food_id': food.id,
                    'food_name': food.name
                })

        return jsonify({'matches': matches})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
