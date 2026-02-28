"""
USDA Database API Endpoints
============================
API endpoints for browsing and searching USDA FoodData Central database.

Endpoints:
- GET /api/v1/usda/search - Search USDA foods with filters
- GET /api/v1/usda/foods - Browse/list USDA foods with pagination and filters
- GET /api/v1/usda/foods/{id} - Get USDA food details with nutrients
- GET /api/v1/usda/categories - Get USDA categories with food counts
"""

from flask import request, jsonify
from sqlalchemy import func

from database import db
from models.usda import USDAFoodCategory, USDAFood, USDANutrient, USDAFoodNutrient, USDAFoodPortion
from routes.api_v1 import bp
from utils.pagination import paginate_query, get_pagination_params
from utils.validators import ValidationError
from utils.auth import require_api_key, require_scope


@bp.route('/usda/search', methods=['GET'])
@require_api_key
@require_scope('read:usda')
def usda_search():
    """
    Search and browse USDA foods with filters (paginated)

    Query Parameters:
    - q (str): Search query for food description
    - category_id (int): Filter by category ID
    - data_type (str): Filter by data type (Foundation, SR Legacy, Survey, Branded)
    - letter (str): Filter by starting letter
    - page (int): Page number (default: 1)
    - per_page (int): Items per page (default: 50, max: 100)

    Returns:
        JSON with paginated results:
        {
            "data": [...],
            "pagination": {
                "page": 1,
                "per_page": 50,
                "total": 1247,
                "pages": 25,
                "has_next": true,
                "has_prev": false
            },
            "filters": {...}
        }

    Example:
        GET /api/v1/usda/search?q=apple&category_id=9&page=1&per_page=20
    """
    try:
        # Get search filters
        query = request.args.get('q', '').strip()
        category_id = request.args.get('category_id', type=int)
        data_type = request.args.get('data_type', '').strip()
        letter = request.args.get('letter', '').upper().strip()

        # Get pagination parameters
        try:
            page, per_page = get_pagination_params(request.args, default_per_page=50, max_per_page=100)
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400

        # Build query
        foods_query = USDAFood.query

        # Filter by search query
        if query:
            foods_query = foods_query.filter(USDAFood.description.ilike(f'%{query}%'))

        # Filter by category
        if category_id:
            foods_query = foods_query.filter_by(category_id=category_id)

        # Filter by data type
        if data_type:
            valid_types = ['Foundation', 'SR Legacy', 'Survey', 'Branded']
            if data_type not in valid_types:
                return jsonify({'error': f'Invalid data_type. Must be one of: {", ".join(valid_types)}'}), 400
            foods_query = foods_query.filter_by(data_type=data_type)

        # Filter by starting letter
        if letter:
            if len(letter) != 1 or not letter.isalpha():
                return jsonify({'error': 'Letter must be a single alphabetic character'}), 400
            foods_query = foods_query.filter(USDAFood.description.ilike(f'{letter}%'))

        # Order by description
        foods_query = foods_query.order_by(USDAFood.description)

        # Apply pagination
        result = paginate_query(foods_query, page=page, per_page=per_page)

        # Add filter metadata
        result['filters'] = {
            'query': query if query else None,
            'category_id': category_id,
            'data_type': data_type if data_type else None,
            'letter': letter if letter else None
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/usda/foods', methods=['GET'])
@require_api_key
@require_scope('read:usda')
def usda_foods_list():
    """
    Get paginated list of USDA foods with optional filtering

    Query Parameters:
    - category_id (int): Filter by category ID
    - data_type (str): Filter by data type (Foundation, SR Legacy, Survey, Branded)
    - letter (str): Filter by starting letter
    - page (int): Page number (default: 1)
    - per_page (int): Items per page (default: 50, max: 100)

    Returns:
        JSON with paginated USDA foods:
        {
            "data": [...],
            "pagination": {...},
            "filters": {...}
        }

    Example:
        GET /api/v1/usda/foods?category_id=9&page=1&per_page=50
    """
    try:
        category_id = request.args.get('category_id', type=int)
        data_type = request.args.get('data_type', '').strip()
        letter = request.args.get('letter', '').upper().strip()

        # Get pagination parameters
        try:
            page, per_page = get_pagination_params(request.args, default_per_page=50, max_per_page=100)
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400

        # Build query
        foods_query = USDAFood.query

        # Filter by category
        if category_id:
            foods_query = foods_query.filter_by(category_id=category_id)

        # Filter by data type
        if data_type:
            valid_types = ['Foundation', 'SR Legacy', 'Survey', 'Branded']
            if data_type not in valid_types:
                return jsonify({'error': f'Invalid data_type. Must be one of: {", ".join(valid_types)}'}), 400
            foods_query = foods_query.filter_by(data_type=data_type)

        # Filter by starting letter
        if letter:
            if len(letter) != 1 or not letter.isalpha():
                return jsonify({'error': 'Letter must be a single alphabetic character'}), 400
            foods_query = foods_query.filter(USDAFood.description.ilike(f'{letter}%'))

        # Order by description
        foods_query = foods_query.order_by(USDAFood.description)

        # Apply pagination
        result = paginate_query(foods_query, page=page, per_page=per_page)

        # Add filter metadata
        result['filters'] = {
            'category_id': category_id,
            'data_type': data_type if data_type else None,
            'letter': letter if letter else None
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/usda/foods/<int:food_id>', methods=['GET'])
@require_api_key
@require_scope('read:usda')
def usda_food_detail(food_id):
    """
    Get detailed information for a specific USDA food

    Args:
        food_id (int): USDA food ID

    Query Parameters:
        include_nutrients (bool): Include nutrients grouped by category (default: true)
        include_portions (bool): Include portion/serving sizes (default: true)

    Returns:
        JSON object with complete food details including:
        - Basic info (id, fdc_id, description, data_type, category)
        - Nutrients grouped by type (Energy, Proximates, Vitamins, Minerals, etc.)
        - Portion sizes with gram weights

    Example:
        GET /api/v1/usda/foods/12345?include_nutrients=true&include_portions=true
    """
    try:
        # Get query parameters
        include_nutrients = request.args.get('include_nutrients', 'true').lower() == 'true'
        include_portions = request.args.get('include_portions', 'true').lower() == 'true'

        # Get food
        food = USDAFood.query.get(food_id)
        if not food:
            return jsonify({'error': f'USDA food with ID {food_id} not found'}), 404

        # Build response
        result = {
            'id': food.id,
            'fdc_id': food.fdc_id,
            'description': food.description,
            'data_type': food.data_type,
            'category': food.category.description if food.category else None,
            'category_id': food.category_id,
            'scientific_name': food.scientific_name,
            'common_names': food.common_names,
            'food_class': food.food_class,
            'publication_date': food.publication_date
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
            result['nutrient_groups'] = ['Energy', 'Proximates', 'Minerals', 'Vitamins', 'Lipids', 'Amino Acids', 'Other']

        # Add portions if requested
        if include_portions:
            portions = []
            for portion in food.portions.order_by(USDAFoodPortion.sequence_number).all():
                portions.append({
                    'id': portion.id,
                    'description': portion.portion_description or portion.get_display_text(),
                    'gram_weight': portion.gram_weight,
                    'amount': portion.amount,
                    'modifier': portion.modifier,
                    'measure_unit': portion.measure_unit
                })
            result['portions'] = portions

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/usda/categories', methods=['GET'])
@require_api_key
@require_scope('read:usda')
def usda_categories():
    """
    Get USDA food categories with food counts

    Query Parameters:
        data_type (str): Filter categories by data type (Foundation, SR Legacy, Survey, Branded)
        min_count (int): Only show categories with at least this many foods (default: 1)

    Returns:
        JSON object with:
        - categories: Array of category objects with id, description, food_count
        - total_foods: Total number of foods across all categories
        - data_type_counts: Breakdown of foods by data type

    Example:
        GET /api/v1/usda/categories?data_type=Foundation&min_count=10
    """
    try:
        data_type = request.args.get('data_type', '').strip()
        min_count = request.args.get('min_count', default=1, type=int)

        # Validate data_type if provided
        if data_type:
            valid_types = ['Foundation', 'SR Legacy', 'Survey', 'Branded']
            if data_type not in valid_types:
                return jsonify({'error': f'Invalid data_type. Must be one of: {", ".join(valid_types)}'}), 400

        # Get categories with food counts
        if data_type:
            # Count foods per category for the selected data type
            category_counts = db.session.query(
                USDAFoodCategory.id,
                USDAFoodCategory.description,
                func.count(USDAFood.id).label('count')
            ).join(USDAFood, USDAFood.category_id == USDAFoodCategory.id
            ).filter(USDAFood.data_type == data_type
            ).group_by(USDAFoodCategory.id, USDAFoodCategory.description
            ).having(func.count(USDAFood.id) >= min_count
            ).order_by(USDAFoodCategory.description).all()

            categories_list = [
                {'id': c.id, 'description': c.description, 'food_count': c.count}
                for c in category_counts
            ]
            total_foods = sum(c['food_count'] for c in categories_list)
        else:
            # Show all categories with their total counts
            all_categories = USDAFoodCategory.query.filter(
                USDAFoodCategory.food_count >= min_count
            ).order_by(USDAFoodCategory.description).all()
            categories_list = [
                {'id': c.id, 'description': c.description, 'food_count': c.food_count}
                for c in all_categories
            ]
            total_foods = USDAFood.query.count()

        # Get counts by data type
        data_type_counts = {
            'Foundation': USDAFood.query.filter_by(data_type='Foundation').count(),
            'SR Legacy': USDAFood.query.filter_by(data_type='SR Legacy').count(),
            'Survey': USDAFood.query.filter_by(data_type='Survey').count(),
            'Branded': USDAFood.query.filter_by(data_type='Branded').count()
        }

        return jsonify({
            'categories': categories_list,
            'count': len(categories_list),
            'total_foods': total_foods,
            'data_type_counts': data_type_counts,
            'filters': {
                'data_type': data_type if data_type else None,
                'min_count': min_count
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
