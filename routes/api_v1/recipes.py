"""
Recipes API v1 Endpoints
Provides API access to recipes and saved meals
"""

from flask import request, jsonify, current_app
from . import bp
from database import db
from models.recipe import Recipe, RecipeIngredient, SavedMeal, SavedMealItem, RecipeClassificationOption
from models.food import Food
from utils import allowed_file
import recipe_categories as rc
from werkzeug.utils import secure_filename
from sqlalchemy import func
from utils.pagination import paginate_query, get_pagination_params
from utils.auth import require_api_key, require_scope
from utils.validators import ValidationError
import os


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def save_upload_file(file, prefix='recipe'):
    """Save uploaded file and return the path"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        filename = f"{prefix}_{timestamp}_{name}{ext}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return f"uploads/{filename}"
    return None


def safe_delete_file(filepath):
    """Safely delete a file, logging errors but not failing the operation"""
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            return True
    except OSError as e:
        current_app.logger.warning(f'Could not delete file {filepath}: {e}')
    return False


def get_classification_options(option_type, base_list, include_value=None):
    """Merge base list with custom options, preserving display order"""
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
    """Resolve custom selections and persist new options for future use"""
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


def process_recipe_classification(data, removed_tags):
    """Process recipe classification fields, filtering removed tags"""
    def filter_tag(value):
        return None if (value and value.strip() in removed_tags) else value

    subcategory = filter_tag(data.get('subcategory'))

    cuisine = resolve_custom_option(
        'cuisine', data.get('cuisine'), data.get('custom_cuisine'), rc.CUISINES
    )
    cuisine = filter_tag(cuisine)

    preparation_method = resolve_custom_option(
        'preparation_method', data.get('preparation_methods'),
        data.get('custom_preparation_method'), rc.PREPARATION_METHODS
    )
    preparation_method = filter_tag(preparation_method)

    occasion = resolve_custom_option(
        'occasion', data.get('occasions'), data.get('custom_occasion'), rc.OCCASIONS
    )
    occasion = filter_tag(occasion)

    difficulty = filter_tag(data.get('difficulty'))

    return {
        'subcategory': subcategory,
        'cuisine': cuisine,
        'preparation_method': preparation_method,
        'occasion': occasion,
        'difficulty': difficulty
    }


def recipe_to_dict(recipe):
    """Convert Recipe object to dictionary"""
    return {
        'id': recipe.id,
        'name': recipe.name,
        'description': recipe.description,
        'servings': recipe.servings,
        'prep_time': recipe.prep_time,
        'cook_time': recipe.cook_time,
        'instructions': recipe.instructions,
        'notes': recipe.notes,
        'category': recipe.category,
        'subcategory': recipe.subcategory,
        'cuisine': recipe.cuisine,
        'dietary_needs': recipe.dietary_needs,
        'preparation_method': recipe.preparation_method,
        'occasion': recipe.occasion,
        'difficulty': recipe.difficulty,
        'tags': recipe.tags,
        'source_url': recipe.source_url,
        'image_path': recipe.image_path,
        'created_at': recipe.created_at.isoformat() if recipe.created_at else None,
        'updated_at': recipe.updated_at.isoformat() if recipe.updated_at else None,
        'ingredients': [ingredient_to_dict(ing) for ing in recipe.ingredients]
    }


def ingredient_to_dict(ingredient):
    """Convert RecipeIngredient to dictionary"""
    food_data = None
    if ingredient.food:
        food_data = {
            'id': ingredient.food.id,
            'name': ingredient.food.name,
            'category': ingredient.food.category
        }

    return {
        'id': ingredient.id,
        'food_id': ingredient.food_id,
        'quantity': ingredient.quantity,
        'notes': ingredient.notes,
        'food': food_data
    }


def saved_meal_to_dict(meal):
    """Convert SavedMeal object to dictionary"""
    return {
        'id': meal.id,
        'name': meal.name,
        'description': meal.description,
        'meal_type': meal.meal_type,
        'image_path': meal.image_path,
        'created_at': meal.created_at.isoformat() if meal.created_at else None,
        'items': [meal_item_to_dict(item) for item in meal.meal_items]
    }


def meal_item_to_dict(item):
    """Convert SavedMealItem to dictionary"""
    food_data = None
    if item.food:
        food_data = {
            'id': item.food.id,
            'name': item.food.name,
            'category': item.food.category
        }

    return {
        'id': item.id,
        'food_id': item.food_id,
        'portion_size': item.portion_size,
        'food': food_data
    }


# =============================================================================
# RECIPE ENDPOINTS
# =============================================================================

@bp.route('/recipes', methods=['GET'])
@require_api_key
@require_scope('read:recipes')
def get_recipes():
    """
    GET /api/v1/recipes
    Get all user-created recipes ordered by created_at (paginated)

    Query Parameters:
        q (str, optional): Search query to filter recipes by name
        page (int, optional): Page number (default: 1)
        per_page (int, optional): Items per page (default: 50, max: 100)

    Returns:
        JSON: Paginated recipe objects with metadata
        {
            "data": [...],
            "pagination": {...}
        }
    """
    try:
        query = request.args.get('q', '').strip()

        # Get pagination parameters
        try:
            page, per_page = get_pagination_params(request.args, default_per_page=50, max_per_page=100)
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400

        # Build query
        recipe_query = Recipe.query

        # Apply search filter if provided
        if query:
            recipe_query = recipe_query.filter(Recipe.name.ilike(f'%{query}%'))

        # Order by created date
        recipe_query = recipe_query.order_by(Recipe.created_at.desc())

        # Apply pagination
        result = paginate_query(recipe_query, page=page, per_page=per_page)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/recipes/search', methods=['GET'])
@require_api_key
@require_scope('read:recipes')
def search_recipes_api():
    """
    GET /api/v1/recipes/search
    Search recipes by name, category, cuisine, tags, or ingredients

    Query Parameters:
        q (str, optional): Search query for recipe name
        category (str, optional): Filter by meal type category
        cuisine (str, optional): Filter by cuisine
        difficulty (str, optional): Filter by difficulty level
        tags (str, optional): Comma-separated tags to filter by
        ingredient (str, optional): Search by ingredient name
        page (int, optional): Page number (default: 1)
        per_page (int, optional): Items per page (default: 50, max: 100)

    Returns:
        JSON: Paginated matching recipes with metadata
    """
    try:
        query = request.args.get('q', '').strip()
        category = request.args.get('category', '').strip()
        cuisine = request.args.get('cuisine', '').strip()
        difficulty = request.args.get('difficulty', '').strip()
        tags = request.args.get('tags', '').strip()
        ingredient = request.args.get('ingredient', '').strip()

        # Get pagination parameters
        try:
            page, per_page = get_pagination_params(request.args, default_per_page=50, max_per_page=100)
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400

        # Build query
        recipe_query = Recipe.query

        # Filter by name search
        if query:
            recipe_query = recipe_query.filter(Recipe.name.ilike(f'%{query}%'))

        # Filter by category
        if category:
            recipe_query = recipe_query.filter(Recipe.category.ilike(category))

        # Filter by cuisine
        if cuisine:
            recipe_query = recipe_query.filter(Recipe.cuisine.ilike(f'%{cuisine}%'))

        # Filter by difficulty
        if difficulty:
            recipe_query = recipe_query.filter(Recipe.difficulty.ilike(f'%{difficulty}%'))

        # Filter by tags
        if tags:
            for tag in tags.split(','):
                tag = tag.strip()
                if tag:
                    recipe_query = recipe_query.filter(Recipe.tags.ilike(f'%{tag}%'))

        # Filter by ingredient name
        if ingredient:
            recipe_query = recipe_query.join(RecipeIngredient).join(Food).filter(
                Food.name.ilike(f'%{ingredient}%')
            )

        # Order by name
        recipe_query = recipe_query.order_by(Recipe.name)

        # Apply pagination
        result = paginate_query(recipe_query, page=page, per_page=per_page)

        # Add filter metadata
        result['filters'] = {
            'q': query if query else None,
            'category': category if category else None,
            'cuisine': cuisine if cuisine else None,
            'difficulty': difficulty if difficulty else None,
            'tags': tags if tags else None,
            'ingredient': ingredient if ingredient else None
        }

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/recipes/category/<category>', methods=['GET'])
@require_api_key
@require_scope('read:recipes')
def get_recipes_by_category(category):
    """
    GET /api/v1/recipes/category/{category}
    Get recipes filtered by meal type category (paginated)

    Query Parameters:
        page (int, optional): Page number (default: 1)
        per_page (int, optional): Items per page (default: 50, max: 100)
    """
    try:
        # Get pagination parameters
        try:
            page, per_page = get_pagination_params(request.args, default_per_page=50, max_per_page=100)
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400

        # Build query
        if category == 'Uncategorized':
            recipe_query = Recipe.query.filter_by(category=None).order_by(Recipe.created_at.desc())
        else:
            recipe_query = Recipe.query.filter_by(category=category).order_by(Recipe.created_at.desc())

        # Apply pagination
        result = paginate_query(recipe_query, page=page, per_page=per_page)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/recipes/<int:recipe_id>', methods=['GET'])
@require_api_key
@require_scope('read:recipes')
def get_recipe(recipe_id):
    """
    GET /api/v1/recipes/{id}
    Get full recipe details with ingredients, instructions, metadata
    """
    try:
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404
        return jsonify(recipe_to_dict(recipe))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/recipes', methods=['POST'])
@require_api_key
@require_scope('write:recipes')
def create_recipe():
    """
    POST /api/v1/recipes
    Create a new recipe with ingredients

    Expected JSON:
    {
        "name": "Recipe Name",
        "description": "Description",
        "servings": 4,
        "prep_time": "15 minutes",
        "cook_time": "30 minutes",
        "instructions": "Step by step...",
        "notes": "Optional notes",
        "category": "Dinner",
        "subcategory": "Main Dish",
        "cuisine": "Italian",
        "dietary_needs": "Gluten-Free, Dairy-Free",
        "preparation_method": "Baking",
        "occasion": "Weeknight Dinner",
        "difficulty": "Beginner-Friendly",
        "tags": "quick, easy",
        "source_url": "https://...",
        "ingredients": [
            {"food_id": 1, "quantity": "100g", "notes": "chopped"},
            {"food_id": 2, "quantity": "2 cups", "notes": ""}
        ]
    }

    Note: Photo upload not supported in JSON API (use form data for photos)
    """
    try:
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({'error': 'Recipe name is required'}), 400

        # Get removed tags
        removed_tags_str = data.get('removed_tags', '')
        removed_tags = set(tag.strip() for tag in removed_tags_str.split(',') if tag.strip())

        # Process dietary needs
        dietary_needs_str = data.get('dietary_needs')
        if dietary_needs_str and removed_tags:
            dietary_needs_list = [need.strip() for need in dietary_needs_str.split(',') if need.strip()]
            dietary_needs_list = [need for need in dietary_needs_list if need not in removed_tags]
            dietary_needs_str = ', '.join(dietary_needs_list) if dietary_needs_list else None

        # Process classification fields
        classification = process_recipe_classification(data, removed_tags)

        # Create recipe
        recipe = Recipe(
            name=data.get('name'),
            description=data.get('description'),
            servings=int(data.get('servings', 1)),
            prep_time=data.get('prep_time'),
            cook_time=data.get('cook_time'),
            instructions=data.get('instructions'),
            notes=data.get('notes'),
            category=data.get('category'),
            subcategory=classification['subcategory'],
            cuisine=classification['cuisine'],
            dietary_needs=dietary_needs_str,
            preparation_method=classification['preparation_method'],
            occasion=classification['occasion'],
            difficulty=classification['difficulty'],
            tags=data.get('tags'),
            source_url=data.get('source_url'),
            image_path=data.get('image_path')
        )
        db.session.add(recipe)
        db.session.flush()

        # Add ingredients
        ingredients = data.get('ingredients', [])
        for ing in ingredients:
            if ing.get('food_id'):
                ingredient = RecipeIngredient(
                    recipe_id=recipe.id,
                    food_id=int(ing['food_id']),
                    quantity=ing.get('quantity', ''),
                    notes=ing.get('notes', '')
                )
                db.session.add(ingredient)

        db.session.commit()
        return jsonify(recipe_to_dict(recipe)), 201

    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/recipes/<int:recipe_id>', methods=['PUT'])
@require_api_key
@require_scope('write:recipes')
def update_recipe(recipe_id):
    """
    PUT /api/v1/recipes/{id}
    Update an existing recipe

    Expected JSON: Same format as POST /api/v1/recipes
    """
    try:
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Get removed tags
        removed_tags_str = data.get('removed_tags', '')
        removed_tags = set(tag.strip() for tag in removed_tags_str.split(',') if tag.strip())

        # Process dietary needs
        dietary_needs_str = data.get('dietary_needs')
        if dietary_needs_str and removed_tags:
            dietary_needs_list = [need.strip() for need in dietary_needs_str.split(',') if need.strip()]
            dietary_needs_list = [need for need in dietary_needs_list if need not in removed_tags]
            dietary_needs_str = ', '.join(dietary_needs_list) if dietary_needs_list else None

        # Process classification fields
        classification = process_recipe_classification(data, removed_tags)

        # Update recipe fields
        recipe.name = data.get('name', recipe.name)
        recipe.description = data.get('description', recipe.description)
        recipe.servings = int(data.get('servings', recipe.servings))
        recipe.prep_time = data.get('prep_time', recipe.prep_time)
        recipe.cook_time = data.get('cook_time', recipe.cook_time)
        recipe.instructions = data.get('instructions', recipe.instructions)
        recipe.notes = data.get('notes', recipe.notes)
        recipe.category = data.get('category', recipe.category)
        recipe.subcategory = classification['subcategory']
        recipe.cuisine = classification['cuisine']
        recipe.dietary_needs = dietary_needs_str
        recipe.preparation_method = classification['preparation_method']
        recipe.occasion = classification['occasion']
        recipe.difficulty = classification['difficulty']
        recipe.tags = data.get('tags', recipe.tags)
        recipe.source_url = data.get('source_url', recipe.source_url)
        if 'image_path' in data:
            recipe.image_path = data['image_path']

        # Replace ingredients if provided
        if 'ingredients' in data:
            RecipeIngredient.query.filter_by(recipe_id=recipe.id).delete()
            for ing in data['ingredients']:
                if ing.get('food_id'):
                    ingredient = RecipeIngredient(
                        recipe_id=recipe.id,
                        food_id=int(ing['food_id']),
                        quantity=ing.get('quantity', ''),
                        notes=ing.get('notes', '')
                    )
                    db.session.add(ingredient)

        db.session.commit()
        return jsonify(recipe_to_dict(recipe))

    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/recipes/<int:recipe_id>', methods=['DELETE'])
@require_api_key
@require_scope('write:recipes')
def delete_recipe(recipe_id):
    """
    DELETE /api/v1/recipes/{id}
    Delete a recipe (cascade deletes ingredients)
    """
    try:
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404

        recipe_name = recipe.name

        # Delete photo file if exists
        if recipe.image_path:
            photo_path = os.path.join(current_app.root_path, 'static', recipe.image_path)
            safe_delete_file(photo_path)

        db.session.delete(recipe)
        db.session.commit()

        return jsonify({'message': f'Recipe "{recipe_name}" deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/recipes/<int:recipe_id>/context', methods=['GET'])
@require_api_key
@require_scope('read:recipes')
def get_recipe_context(recipe_id):
    """
    GET /api/v1/recipes/{id}/context
    Get full recipe details formatted for AI context

    Returns:
        JSON: Recipe object with all details formatted for AI processing
        Includes: name, description, category, cuisine, servings, prep_time,
        cook_time, ingredients (with quantities and notes), instructions,
        notes, dietary_needs, difficulty

    Use Case:
        Provides structured recipe data for AI chat context or analysis
    """
    try:
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404

        # Get ingredients with food details
        ingredients_list = []
        for ing in recipe.ingredients:
            food_name = ing.food.name if ing.food else 'Unknown'
            quantity = ing.quantity or ''
            notes = ing.notes or ''
            ingredient_str = f"{quantity} {food_name}".strip()
            if notes:
                ingredient_str += f" ({notes})"
            ingredients_list.append(ingredient_str)

        return jsonify({
            'id': recipe.id,
            'name': recipe.name,
            'description': recipe.description or '',
            'category': recipe.category or '',
            'cuisine': recipe.cuisine or '',
            'servings': recipe.servings,
            'prep_time': recipe.prep_time or '',
            'cook_time': recipe.cook_time or '',
            'ingredients': ingredients_list,
            'instructions': recipe.instructions or '',
            'notes': recipe.notes or '',
            'dietary_needs': recipe.dietary_needs or '',
            'difficulty': recipe.difficulty or ''
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================================================
# SAVED MEAL ENDPOINTS
# =============================================================================

@bp.route('/meals', methods=['GET'])
@require_api_key
@require_scope('read:recipes')
def get_meals():
    """
    GET /api/v1/meals
    Get all saved meals ordered by created_at
    """
    try:
        meals = SavedMeal.query.order_by(SavedMeal.created_at.desc()).all()
        return jsonify([saved_meal_to_dict(m) for m in meals])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/meals', methods=['POST'])
@require_api_key
@require_scope('write:recipes')
def saved_meal_create():
    """
    POST /api/v1/meals
    Create a new saved meal

    Expected JSON:
    {
        "name": "Meal Name",
        "description": "Description",
        "meal_type": "Breakfast",
        "items": [
            {"food_id": 1, "portion_size": "100g"},
            {"food_id": 2, "portion_size": "1 cup"}
        ]
    }

    Note: Photo upload not supported in JSON API (use form data for photos)
    """
    try:
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({'error': 'Meal name is required'}), 400

        # Create saved meal
        meal = SavedMeal(
            name=data.get('name'),
            description=data.get('description'),
            meal_type=data.get('meal_type'),
            image_path=data.get('image_path')
        )
        db.session.add(meal)
        db.session.flush()

        # Add meal items
        items = data.get('items', [])
        for item in items:
            if item.get('food_id'):
                meal_item = SavedMealItem(
                    saved_meal_id=meal.id,
                    food_id=int(item['food_id']),
                    portion_size=item.get('portion_size', '')
                )
                db.session.add(meal_item)

        db.session.commit()
        return jsonify(saved_meal_to_dict(meal)), 201

    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/meals/<int:meal_id>', methods=['PUT'])
@require_api_key
@require_scope('write:recipes')
def saved_meal_update(meal_id):
    """
    PUT /api/v1/meals/{id}
    Update an existing saved meal

    Expected JSON: Same format as POST /api/v1/meals
    """
    try:
        meal = SavedMeal.query.get(meal_id)
        if not meal:
            return jsonify({'error': 'Meal not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Update meal fields
        meal.name = data.get('name', meal.name)
        meal.description = data.get('description', meal.description)
        meal.meal_type = data.get('meal_type', meal.meal_type)
        if 'image_path' in data:
            meal.image_path = data['image_path']

        # Replace meal items if provided
        if 'items' in data:
            SavedMealItem.query.filter_by(saved_meal_id=meal.id).delete()
            for item in data['items']:
                if item.get('food_id'):
                    meal_item = SavedMealItem(
                        saved_meal_id=meal.id,
                        food_id=int(item['food_id']),
                        portion_size=item.get('portion_size', '')
                    )
                    db.session.add(meal_item)

        db.session.commit()
        return jsonify(saved_meal_to_dict(meal))

    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/meals/<int:meal_id>', methods=['DELETE'])
@require_api_key
@require_scope('write:recipes')
def saved_meal_delete(meal_id):
    """
    DELETE /api/v1/meals/{id}
    Delete a saved meal (cascade deletes items)
    """
    try:
        meal = SavedMeal.query.get(meal_id)
        if not meal:
            return jsonify({'error': 'Meal not found'}), 404

        meal_name = meal.name

        # Delete photo file if exists
        if meal.image_path:
            photo_path = os.path.join('static', meal.image_path.lstrip('/'))
            safe_delete_file(photo_path)

        db.session.delete(meal)
        db.session.commit()

        return jsonify({'message': f'Meal "{meal_name}" deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# =============================================================================
# PHASE 3: BATCH OPERATIONS ENDPOINT
# =============================================================================

@bp.route('/recipes/import', methods=['POST'])
@require_api_key
@require_scope('write:recipes')
def import_recipe():
    """
    POST /api/v1/recipes/import
    Import recipe from external JSON format

    Expected JSON:
    {
        "recipe_json": {
            "name": "Recipe Name",
            "description": "Description",
            "meal_type": "Lunch",
            "servings": 4,
            "prep_time": "15 mins",
            "cook_time": "30 mins",
            "ingredients": [
                {"name": "Apple", "amount": "2 medium", "category": "Fruit"},
                {"name": "Flour", "amount": "200g", "category": "Grains"}
            ],
            "instructions": "Step 1: Do this\\nStep 2: Do that",
            "tags": ["quick", "healthy"]
        }
    }

    OR (for future URL import - not yet implemented):
    {
        "url": "https://example.com/recipe/123"
    }

    Returns:
    {
        "success": true,
        "recipe_id": 123,
        "name": "Recipe Name",
        "matched_ingredients": 5,
        "unmatched_ingredients": [
            {"name": "Exotic Fruit", "suggested_category": "Fruit"}
        ],
        "message": "Recipe imported successfully"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Check if URL import (not yet implemented)
        if 'url' in data:
            return jsonify({
                'error': 'URL import not yet implemented. Please use recipe_json format.'
            }), 501  # Not Implemented

        # Handle JSON import
        if 'recipe_json' not in data:
            return jsonify({'error': 'recipe_json is required'}), 400

        recipe_data = data['recipe_json']

        # Validate required fields
        required_fields = ['name', 'ingredients', 'instructions']
        missing_fields = [f for f in required_fields if f not in recipe_data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        # Extract recipe metadata
        recipe_name = recipe_data['name']
        description = recipe_data.get('description', '')
        meal_type = recipe_data.get('meal_type', 'Other')
        servings = recipe_data.get('servings', 1)
        prep_time = recipe_data.get('prep_time', '')
        cook_time = recipe_data.get('cook_time', '')
        instructions = recipe_data.get('instructions', '')
        tags = recipe_data.get('tags', [])

        # Process ingredients - try to match with food library
        ingredients_list = recipe_data.get('ingredients', [])
        matched_ingredients = []
        unmatched_ingredients = []

        for ing_data in ingredients_list:
            ing_name = ing_data.get('name', '').strip()
            ing_amount = ing_data.get('amount', '').strip()
            ing_category = ing_data.get('category', '').strip()

            if not ing_name:
                continue

            # Try to find matching food in database
            # First try exact match
            food = Food.query.filter(Food.name.ilike(ing_name)).first()

            if not food:
                # Try partial match
                food = Food.query.filter(Food.name.ilike(f'%{ing_name}%')).first()

            if food:
                matched_ingredients.append({
                    'food_id': food.id,
                    'food_name': food.name,
                    'quantity': ing_amount,
                    'original_name': ing_name
                })
            else:
                unmatched_ingredients.append({
                    'name': ing_name,
                    'amount': ing_amount,
                    'suggested_category': ing_category or 'Other'
                })

        # Create the recipe
        recipe = Recipe(
            name=recipe_name,
            description=description,
            category=meal_type,
            servings=servings,
            prep_time=prep_time,
            cook_time=cook_time,
            instructions=instructions
        )
        db.session.add(recipe)
        db.session.flush()  # Get recipe ID

        # Add matched ingredients to recipe
        from models.recipe import RecipeIngredient
        for ing in matched_ingredients:
            recipe_ing = RecipeIngredient(
                recipe_id=recipe.id,
                food_id=ing['food_id'],
                quantity=ing['quantity']
            )
            db.session.add(recipe_ing)

        # Add tags (stored as comma-separated string on Recipe.tags)
        if tags:
            cleaned_tags = [t.strip() for t in tags if isinstance(t, str) and t.strip()]
            if cleaned_tags:
                recipe.tags = ', '.join(cleaned_tags)

        db.session.commit()

        # Build response
        response = {
            'success': True,
            'recipe_id': recipe.id,
            'name': recipe.name,
            'matched_ingredients': len(matched_ingredients),
            'unmatched_ingredients': unmatched_ingredients,
            'message': f'Recipe "{recipe_name}" imported successfully'
        }

        if unmatched_ingredients:
            response['warning'] = (
                f'{len(unmatched_ingredients)} ingredients could not be matched to food library. '
                'You may need to add them manually or edit the recipe.'
            )

        return jsonify(response), 201

    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# =============================================================================
# 2 NEW RECIPE ENDPOINTS FOR APP2 INTEGRATION
# =============================================================================

@bp.route('/recipes/<int:recipe_id>/transform', methods=['POST'])
@require_api_key
@require_scope('write:recipes')
def transform_recipe(recipe_id):
    """
    POST /api/v1/recipes/<int:recipe_id>/transform
    Auto-substitute high-risk ingredients with safer alternatives
    Does NOT modify the recipe, only returns suggestions
    """
    try:
        from routes.api_v1.analytics import get_traffic_light_color
        from models.recipe import Recipe

        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({'error': f'Recipe {recipe_id} not found'}), 404

        substitutions = []
        safe_ingredient_count = 0
        flagged_ingredient_count = 0

        for ingredient in recipe.ingredients:
            food = ingredient.food
            if not food:
                continue

            # Get risk level for safe serving type
            safe_color = get_traffic_light_color(food, 'safe')

            if safe_color in ['amber', 'red']:
                flagged_ingredient_count += 1

                # Find safer alternatives in same category
                alternatives = Food.query.filter(
                    Food.category == food.category,
                    Food.id != food.id,
                    Food.safe_traffic_light == 'Green'
                ).limit(3).all()

                suggestion_list = []
                for alt_food in alternatives:
                    alt_color = get_traffic_light_color(alt_food, 'safe')
                    if alt_color == 'green':
                        suggestion_list.append({
                            'food_id': alt_food.id,
                            'food_name': alt_food.name,
                            'risk': 'green',
                            'quantity_note': f'Use similar quantity as {food.name}'
                        })

                substitutions.append({
                    'original': {
                        'food_id': food.id,
                        'food_name': food.name,
                        'risk': safe_color
                    },
                    'suggestions': suggestion_list
                })
            else:
                safe_ingredient_count += 1

        # Determine overall risk
        if flagged_ingredient_count == 0:
            risk_level = 'low'
        elif flagged_ingredient_count <= 2:
            risk_level = 'moderate'
        else:
            risk_level = 'high'

        return jsonify({
            'recipe_id': recipe_id,
            'recipe_name': recipe.name,
            'original_risk_level': risk_level,
            'substitutions': substitutions,
            'safe_ingredient_count': safe_ingredient_count,
            'flagged_ingredient_count': flagged_ingredient_count,
            'message': 'Suggestions generated. Recipe not modified.'
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/recipes/share', methods=['POST'])
@require_api_key
@require_scope('write:recipes')
def share_recipe():
    """
    POST /api/v1/recipes/share
    Export recipe as shareable JSON payload with unique token
    Input: {"recipe_id": 5, "include_notes": true}
    """
    try:
        from models.recipe import Recipe, RecipeShare
        import uuid

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400

        recipe_id = data.get('recipe_id')
        include_notes = data.get('include_notes', False)

        if not recipe_id:
            return jsonify({'error': 'recipe_id is required'}), 400

        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({'error': f'Recipe {recipe_id} not found'}), 404

        # Generate unique share token
        share_token = str(uuid.uuid4())

        # Create RecipeShare record
        recipe_share = RecipeShare(
            recipe_id=recipe_id,
            share_token=share_token
        )
        db.session.add(recipe_share)
        db.session.commit()

        # Build full recipe dict for import
        recipe_dict = recipe.to_dict()

        return jsonify({
            'share_token': share_token,
            'recipe_id': recipe_id,
            'recipe_name': recipe.name,
            'token_expires_at': None,
            'import_instructions': 'Use this token with POST /api/v1/recipes/import to import this recipe',
            'recipe': recipe_dict if include_notes else {k: v for k, v in recipe_dict.items() if k != 'notes'}
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
