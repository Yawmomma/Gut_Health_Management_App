"""
Search & Discovery API v1 Endpoints
Provides global search and recommendation capabilities
"""

from flask import request, jsonify
from . import bp
from database import db
from models.food import Food
from models.recipe import Recipe, SavedMeal, RecipeIngredient
from models.education import EducationalContent, HelpDocument
from sqlalchemy import or_
from utils.auth import require_api_key, require_scope


# =============================================================================
# PHASE 3: SEARCH & DISCOVERY ENDPOINTS
# =============================================================================

@bp.route('/search/global', methods=['GET'])
@require_api_key
@require_scope('read:search')
def global_search():
    """
    GET /api/v1/search/global?q={query}&types=foods,recipes
    Search across foods, recipes, saved meals, help docs, and education content

    Query Parameters:
    - q: Search query (required, min 2 characters)
    - types: Comma-separated list of types to search (optional, default: all)
      Options: foods, recipes, meals, help, education
    - limit: Results per type (default: 10, max: 50)

    Returns:
    {
        "query": "apple",
        "types_searched": ["foods", "recipes", "meals", "help", "education"],
        "results": {
            "foods": [
                {"id": 123, "name": "Apple", "category": "Fruit", "type": "food"},
                ...
            ],
            "recipes": [
                {"id": 45, "name": "Apple Pie", "meal_type": "Dessert", "type": "recipe"},
                ...
            ],
            "meals": [...],
            "help": [...],
            "education": [...]
        },
        "total_results": 23
    }
    """
    try:
        query = request.args.get('q', '').strip()
        types_str = request.args.get('types', '').strip()
        limit = int(request.args.get('limit', 10))

        if not query:
            return jsonify({'error': 'Query parameter "q" is required'}), 400

        if len(query) < 2:
            return jsonify({'error': 'Query must be at least 2 characters'}), 400

        if limit < 1:
            limit = 10
        if limit > 50:
            limit = 50

        # Determine which types to search
        all_types = ['foods', 'recipes', 'meals', 'help', 'education']
        if types_str:
            types_to_search = [t.strip() for t in types_str.split(',') if t.strip() in all_types]
        else:
            types_to_search = all_types

        results = {}
        total_count = 0

        # Search Foods
        if 'foods' in types_to_search:
            foods = Food.query.filter(
                Food.usda_food_id.is_(None),
                Food.ausnut_food_id.is_(None),
                or_(
                    Food.name.ilike(f'%{query}%'),
                    Food.category.ilike(f'%{query}%')
                )
            ).limit(limit).all()

            results['foods'] = [{
                'id': f.id,
                'name': f.name,
                'category': f.category,
                'type': 'food',
                'traffic_light': f.safe_traffic_light or 'unknown'
            } for f in foods]
            total_count += len(foods)

        # Search Recipes
        if 'recipes' in types_to_search:
            recipes = Recipe.query.filter(
                or_(
                    Recipe.name.ilike(f'%{query}%'),
                    Recipe.description.ilike(f'%{query}%'),
                    Recipe.category.ilike(f'%{query}%')
                )
            ).limit(limit).all()

            results['recipes'] = [{
                'id': r.id,
                'name': r.name,
                'category': r.category,
                'servings': r.servings,
                'type': 'recipe',
                'description': r.description[:100] + '...' if r.description and len(r.description) > 100 else r.description
            } for r in recipes]
            total_count += len(recipes)

        # Search Saved Meals
        if 'meals' in types_to_search:
            meals = SavedMeal.query.filter(
                or_(
                    SavedMeal.name.ilike(f'%{query}%'),
                    SavedMeal.description.ilike(f'%{query}%'),
                    SavedMeal.meal_type.ilike(f'%{query}%')
                )
            ).limit(limit).all()

            results['meals'] = [{
                'id': m.id,
                'name': m.name,
                'meal_type': m.meal_type,
                'type': 'saved_meal',
                'description': m.description[:100] + '...' if m.description and len(m.description) > 100 else m.description
            } for m in meals]
            total_count += len(meals)

        # Search Help Documents
        if 'help' in types_to_search:
            help_docs = HelpDocument.query.filter(
                or_(
                    HelpDocument.title.ilike(f'%{query}%'),
                    HelpDocument.content.ilike(f'%{query}%')
                )
            ).limit(limit).all()

            results['help'] = [{
                'id': h.id,
                'title': h.title,
                'category': h.category,
                'type': 'help'
            } for h in help_docs]
            total_count += len(help_docs)

        # Search Education Content
        if 'education' in types_to_search:
            chapters = EducationalContent.query.filter(
                or_(
                    EducationalContent.title.ilike(f'%{query}%'),
                    EducationalContent.content.ilike(f'%{query}%')
                )
            ).limit(limit).all()

            results['education'] = [{
                'id': c.id,
                'title': c.title,
                'chapter_number': c.chapter_number,
                'section': c.section,
                'type': 'education'
            } for c in chapters]
            total_count += len(chapters)

        return jsonify({
            'query': query,
            'types_searched': types_to_search,
            'results': results,
            'total_results': total_count
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/foods/recommendations', methods=['GET'])
@require_api_key
@require_scope('read:foods')
def get_food_recommendations():
    """
    GET /api/v1/foods/recommendations?avoid=fructans,lactose&histamine_level=low&limit=20
    Get safe foods based on dietary restrictions

    Query Parameters:
    - avoid: Comma-separated FODMAP types to avoid (optional)
      Options: fructose, sorbitol, lactose, gos, fructans, mannitol, polyols
    - histamine_level: Maximum histamine level (optional: low, medium, high)
    - dao_blocker: Avoid DAO blockers (optional: true/false, default: true)
    - liberator: Avoid histamine liberators (optional: true/false, default: true)
    - category: Filter by food category (optional)
    - limit: Number of results (default: 20, max: 100)

    Returns:
    {
        "restrictions": {
            "avoid_fodmap": ["fructans", "lactose"],
            "histamine_level": "low",
            "dao_blocker": true,
            "liberator": true
        },
        "foods": [
            {
                "id": 123,
                "name": "Apple",
                "category": "Fruit",
                "safe_serving_size": "1 medium",
                "traffic_light": "green",
                "notes": "Safe at 1 medium serving"
            },
            ...
        ],
        "total_count": 45
    }
    """
    try:
        avoid_str = request.args.get('avoid', '').strip()
        histamine_level = request.args.get('histamine_level', '').strip().lower()
        dao_blocker = request.args.get('dao_blocker', 'true').lower() == 'true'
        liberator = request.args.get('liberator', 'true').lower() == 'true'
        category = request.args.get('category', '').strip()
        limit = int(request.args.get('limit', 20))

        if limit < 1:
            limit = 20
        if limit > 100:
            limit = 100

        # Parse FODMAPs to avoid
        avoid_fodmaps = []
        if avoid_str:
            avoid_fodmaps = [f.strip() for f in avoid_str.split(',') if f.strip()]

        # Start with FODMAP-only foods (exclude USDA/AUSNUT imports)
        query = Food.query.filter(Food.usda_food_id.is_(None), Food.ausnut_food_id.is_(None))

        # Filter by category if provided
        if category:
            query = query.filter(Food.category == category)

        # Get foods
        all_foods = query.all()

        # Filter foods based on restrictions
        safe_foods = []
        for food in all_foods:
            is_safe = True

            # Check FODMAP restrictions on SAFE serving size
            for fodmap_type in avoid_fodmaps:
                fodmap_attr = f'safe_{fodmap_type}'
                if hasattr(food, fodmap_attr):
                    rating = getattr(food, fodmap_attr)
                    if rating and rating.lower() in ['red', 'high', 'amber', 'medium', 'moderate']:
                        is_safe = False
                        break

            if not is_safe:
                continue

            # Check histamine level on SAFE serving size
            if histamine_level:
                safe_histamine = food.safe_histamine_level
                if safe_histamine:
                    safe_histamine_lower = safe_histamine.lower()
                    if histamine_level == 'low':
                        if safe_histamine_lower in ['medium', 'moderate', 'high']:
                            is_safe = False
                    elif histamine_level == 'medium':
                        if safe_histamine_lower in ['high']:
                            is_safe = False

            if not is_safe:
                continue

            # Check DAO blocker
            if dao_blocker:
                if food.safe_dao_blocker and food.safe_dao_blocker.lower() == 'yes':
                    is_safe = False

            if not is_safe:
                continue

            # Check histamine liberator
            if liberator:
                if food.safe_histamine_liberator and food.safe_histamine_liberator.lower() == 'yes':
                    is_safe = False

            if is_safe:
                # Build safe serving size string
                safe_serving_display = f"{food.safe_serving} {food.safe_serving_unit}".strip() if food.safe_serving else None

                safe_foods.append({
                    'id': food.id,
                    'name': food.name,
                    'category': food.category,
                    'safe_serving': safe_serving_display,
                    'traffic_light': food.safe_traffic_light or 'unknown',
                    'notes': f'Safe at {safe_serving_display}' if safe_serving_display else 'Check serving sizes'
                })

        # Sort alphabetically
        safe_foods.sort(key=lambda x: x['name'])

        # Limit results
        safe_foods = safe_foods[:limit]

        return jsonify({
            'restrictions': {
                'avoid_fodmap': avoid_fodmaps,
                'histamine_level': histamine_level if histamine_level else None,
                'dao_blocker': dao_blocker,
                'liberator': liberator,
                'category': category if category else None
            },
            'foods': safe_foods,
            'total_count': len(safe_foods)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/recipes/suitable', methods=['GET'])
@require_api_key
@require_scope('read:recipes')
def get_suitable_recipes():
    """
    GET /api/v1/recipes/suitable?fodmap_safe=true&histamine_level=low&meal_type=Lunch
    Get recipes matching dietary restrictions

    Query Parameters:
    - fodmap_safe: Only include recipes with all safe FODMAP ingredients (default: false)
    - histamine_level: Maximum histamine level (optional: low, medium, high)
    - meal_type: Filter by meal type (optional)
    - avoid: Comma-separated FODMAP types to avoid (optional)
    - limit: Number of results (default: 20, max: 50)

    Returns:
    {
        "restrictions": {
            "fodmap_safe": true,
            "histamine_level": "low",
            "avoid_fodmap": ["fructans"],
            "meal_type": "Lunch"
        },
        "recipes": [
            {
                "id": 45,
                "name": "Grilled Chicken Salad",
                "meal_type": "Lunch",
                "servings": 4,
                "ingredients_count": 8,
                "suitability": {
                    "safe_ingredients": 8,
                    "moderate_ingredients": 0,
                    "high_risk_ingredients": 0
                }
            },
            ...
        ],
        "total_count": 12
    }
    """
    try:
        fodmap_safe = request.args.get('fodmap_safe', 'false').lower() == 'true'
        histamine_level = request.args.get('histamine_level', '').strip().lower()
        meal_type = request.args.get('meal_type', '').strip()
        avoid_str = request.args.get('avoid', '').strip()
        limit = int(request.args.get('limit', 20))

        if limit < 1:
            limit = 20
        if limit > 50:
            limit = 50

        # Parse FODMAPs to avoid
        avoid_fodmaps = []
        if avoid_str:
            avoid_fodmaps = [f.strip() for f in avoid_str.split(',') if f.strip()]

        # Start with all recipes
        query = Recipe.query

        # Filter by category if provided
        if meal_type:
            query = query.filter(Recipe.category == meal_type)

        recipes = query.all()

        # Evaluate each recipe for suitability
        suitable_recipes = []

        for recipe in recipes:
            # Get recipe ingredients
            ingredients = RecipeIngredient.query.filter_by(recipe_id=recipe.id).all()

            if len(ingredients) == 0:
                continue  # Skip recipes with no ingredients

            safe_count = 0
            moderate_count = 0
            high_risk_count = 0
            is_suitable = True

            for ingredient in ingredients:
                food = ingredient.food
                if not food:
                    continue

                # Check FODMAP safety (using safe serving as default)
                food_is_safe = True

                # Check FODMAPs to avoid
                for fodmap_type in avoid_fodmaps:
                    fodmap_attr = f'safe_{fodmap_type}'
                    if hasattr(food, fodmap_attr):
                        rating = getattr(food, fodmap_attr)
                        if rating and rating.lower() in ['red', 'high']:
                            food_is_safe = False
                            high_risk_count += 1
                            break
                        elif rating and rating.lower() in ['amber', 'medium', 'moderate']:
                            moderate_count += 1
                            food_is_safe = False
                            break

                # Check histamine level
                if food_is_safe and histamine_level:
                    safe_histamine = food.safe_histamine_level
                    if safe_histamine:
                        safe_histamine_lower = safe_histamine.lower()
                        if histamine_level == 'low':
                            if safe_histamine_lower in ['medium', 'moderate']:
                                moderate_count += 1
                                food_is_safe = False
                            elif safe_histamine_lower in ['high']:
                                high_risk_count += 1
                                food_is_safe = False
                        elif histamine_level == 'medium':
                            if safe_histamine_lower in ['high']:
                                high_risk_count += 1
                                food_is_safe = False

                if food_is_safe:
                    safe_count += 1

            # Determine if recipe meets criteria
            if fodmap_safe and (moderate_count > 0 or high_risk_count > 0):
                is_suitable = False

            if is_suitable:
                suitable_recipes.append({
                    'id': recipe.id,
                    'name': recipe.name,
                    'category': recipe.category,
                    'servings': recipe.servings,
                    'prep_time': recipe.prep_time,
                    'cook_time': recipe.cook_time,
                    'ingredients_count': len(ingredients),
                    'suitability': {
                        'safe_ingredients': safe_count,
                        'moderate_ingredients': moderate_count,
                        'high_risk_ingredients': high_risk_count,
                        'percentage_safe': round((safe_count / len(ingredients)) * 100, 1) if len(ingredients) > 0 else 0
                    }
                })

        # Sort by percentage safe (highest first)
        suitable_recipes.sort(key=lambda x: x['suitability']['percentage_safe'], reverse=True)

        # Limit results
        suitable_recipes = suitable_recipes[:limit]

        return jsonify({
            'restrictions': {
                'fodmap_safe': fodmap_safe,
                'histamine_level': histamine_level if histamine_level else None,
                'avoid_fodmap': avoid_fodmaps,
                'meal_type': meal_type if meal_type else None
            },
            'recipes': suitable_recipes,
            'total_count': len(suitable_recipes)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
