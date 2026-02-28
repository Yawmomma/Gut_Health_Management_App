"""
AUSNUT Database API Endpoints
==============================
API endpoints for browsing and searching AUSNUT 2023 Australian food database.

Endpoints:
- GET /api/v1/ausnut/search - Search AUSNUT foods with filters
- GET /api/v1/ausnut/foods/{id} - Get AUSNUT food details with nutrients
"""

from flask import request, jsonify
from sqlalchemy import func

from database import db
from models.ausnut import AUSNUTFood, AUSNUTNutrient, AUSNUTFoodNutrient
from routes.api_v1 import bp
from utils.auth import require_api_key, require_scope


@bp.route('/ausnut/search', methods=['GET'])
@require_api_key
@require_scope('read:ausnut')
def ausnut_search():
    """
    Search and browse AUSNUT 2023 Australian foods with filters

    Query Parameters:
    - q (str): Search query for food name
    - letter (str): Filter by starting letter
    - limit (int): Maximum results to return (default 500, max 1000)

    Returns:
        JSON array of food objects with basic details

    Example:
        GET /api/v1/ausnut/search?q=bread&letter=B&limit=50
    """
    try:
        query = request.args.get('q', '').strip()
        letter = request.args.get('letter', '').upper().strip()
        limit = request.args.get('limit', default=500, type=int)

        # Validate limit
        if limit < 1 or limit > 1000:
            return jsonify({'error': 'Limit must be between 1 and 1000'}), 400

        # Build query
        foods_query = AUSNUTFood.query

        # Filter by search query
        if query:
            foods_query = foods_query.filter(AUSNUTFood.food_name.ilike(f'%{query}%'))

        # Filter by starting letter
        if letter:
            if len(letter) != 1 or not letter.isalpha():
                return jsonify({'error': 'Letter must be a single alphabetic character'}), 400
            foods_query = foods_query.filter(AUSNUTFood.food_name.ilike(f'{letter}%'))

        # Order by food name
        foods_query = foods_query.order_by(AUSNUTFood.food_name)

        # Apply limit
        foods = foods_query.limit(limit).all()

        # Serialize results
        results = []
        for food in foods:
            results.append({
                'id': food.id,
                'survey_id': food.survey_id,
                'public_food_key': food.public_food_key,
                'food_name': food.food_name,
                'derivation': food.derivation
            })

        return jsonify({
            'foods': results,
            'count': len(results),
            'limit': limit,
            'filters': {
                'query': query if query else None,
                'letter': letter if letter else None
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/ausnut/foods/<int:food_id>', methods=['GET'])
@require_api_key
@require_scope('read:ausnut')
def ausnut_food_detail(food_id):
    """
    Get detailed information for a specific AUSNUT food

    Args:
        food_id (int): AUSNUT food ID

    Query Parameters:
        include_nutrients (bool): Include nutrients grouped by category (default: true)

    Returns:
        JSON object with complete food details including:
        - Basic info (id, survey_id, food_name, derivation)
        - Nutrients grouped by type (Energy, Macronutrients, Vitamins, Minerals, etc.)

    Example:
        GET /api/v1/ausnut/foods/12345?include_nutrients=true
    """
    try:
        # Get query parameters
        include_nutrients = request.args.get('include_nutrients', 'true').lower() == 'true'

        # Get food
        food = AUSNUTFood.query.get(food_id)
        if not food:
            return jsonify({'error': f'AUSNUT food with ID {food_id} not found'}), 404

        # Build response
        result = {
            'id': food.id,
            'survey_id': food.survey_id,
            'public_food_key': food.public_food_key,
            'food_name': food.food_name,
            'derivation': food.derivation
        }

        # Add nutrients if requested
        if include_nutrients:
            nutrients_by_group = {}
            for fn in food.nutrients:
                if fn.nutrient and fn.amount is not None:
                    group = fn.nutrient.nutrient_group or 'Other'
                    if group not in nutrients_by_group:
                        nutrients_by_group[group] = []
                    nutrients_by_group[group].append({
                        'name': fn.nutrient.name,
                        'amount': fn.amount,
                        'unit': fn.nutrient.unit_name,
                        'rank': fn.nutrient.rank or 999
                    })

            # Sort nutrients within each group by rank
            for group in nutrients_by_group:
                nutrients_by_group[group].sort(key=lambda x: (x['rank'], x['name']))

            result['nutrients_by_group'] = nutrients_by_group
            result['nutrient_groups'] = ['Energy', 'Macronutrients', 'Vitamins', 'Minerals', 'Fats', 'Other']

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
