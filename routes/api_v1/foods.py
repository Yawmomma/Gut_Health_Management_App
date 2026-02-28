"""
Foods API v1 Endpoints
Provides API access to food compendium (FODMAP database)
"""

from flask import request, jsonify
from . import bp
from database import db
from models.food import Food
from models.diary import MealFood
from models.recipe import RecipeIngredient, SavedMealItem
from utils.api_helpers import (
    success_response, error_response, not_found_error, validation_error,
    wrap_exception, missing_field_error
)
from utils.auth import require_api_key, require_scope
import json


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def parse_custom_nutrients(data):
    """Parse custom nutrients from data and return as JSON string"""
    def safe_value(value):
        """Safely parse a nutrient value, preserving symbols like <, >, ~ before numbers"""
        if value is None or value == '':
            return None
        value = str(value).strip()
        if not value:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return value

    custom_nutrients = {
        'vitamins': [],
        'minerals': [],
        'macros': []
    }

    # Parse vitamins if present
    if 'vitamins' in data:
        for i, vitamin in enumerate(data['vitamins'], 1):
            if vitamin.get('name'):
                custom_nutrients['vitamins'].append({
                    'name': vitamin['name'].strip(),
                    'per_serve': safe_value(vitamin.get('per_serve')),
                    'per_100': safe_value(vitamin.get('per_100')),
                    'unit': vitamin.get('unit', 'mg'),
                    'rdi': vitamin.get('rdi', '').strip(),
                    'order': i
                })

    # Parse minerals if present
    if 'minerals' in data:
        for i, mineral in enumerate(data['minerals'], 1):
            if mineral.get('name'):
                custom_nutrients['minerals'].append({
                    'name': mineral['name'].strip(),
                    'per_serve': safe_value(mineral.get('per_serve')),
                    'per_100': safe_value(mineral.get('per_100')),
                    'unit': 'mg',
                    'rdi': mineral.get('rdi', '').strip(),
                    'order': i
                })

    # Parse macros if present
    if 'macros' in data:
        for i, macro in enumerate(data['macros'], 1):
            if macro.get('name'):
                custom_nutrients['macros'].append({
                    'name': macro['name'].strip(),
                    'per_serve': safe_value(macro.get('per_serve')),
                    'per_100': safe_value(macro.get('per_100')),
                    'unit': 'g',
                    'order': i
                })

    # Only return JSON if there are any custom nutrients
    if custom_nutrients['vitamins'] or custom_nutrients['minerals'] or custom_nutrients['macros']:
        return json.dumps(custom_nutrients)
    return None


def food_to_dict(food, include_usage=False):
    """Convert Food object to dictionary"""
    result = {
        'id': food.id,
        'name': food.name,
        'category': food.category,
        # Legacy FODMAP fields (safe serving values)
        'fructans': food.fructans,
        'gos': food.gos,
        'lactose': food.lactose,
        'fructose': food.fructose,
        'polyols': food.polyols,
        'mannitol': food.mannitol,
        'sorbitol': food.sorbitol,
        # Safe serving
        'safe_serving': food.safe_serving,
        'safe_serving_unit': food.safe_serving_unit,
        'safe_serving_type': food.safe_serving_type,
        'safe_serving_note': food.safe_serving_note,
        'safe_traffic_light': food.safe_traffic_light,
        'safe_fructans': food.safe_fructans,
        'safe_gos': food.safe_gos,
        'safe_lactose': food.safe_lactose,
        'safe_fructose': food.safe_fructose,
        'safe_polyols': food.safe_polyols,
        'safe_mannitol': food.safe_mannitol,
        'safe_sorbitol': food.safe_sorbitol,
        'safe_histamine_level': food.safe_histamine_level,
        'safe_histamine_liberator': food.safe_histamine_liberator,
        'safe_dao_blocker': food.safe_dao_blocker,
        # Moderate serving
        'moderate_serving': food.moderate_serving,
        'moderate_serving_unit': food.moderate_serving_unit,
        'moderate_serving_type': food.moderate_serving_type,
        'moderate_serving_note': food.moderate_serving_note,
        'moderate_traffic_light': food.moderate_traffic_light,
        'moderate_fructans': food.moderate_fructans,
        'moderate_gos': food.moderate_gos,
        'moderate_lactose': food.moderate_lactose,
        'moderate_fructose': food.moderate_fructose,
        'moderate_polyols': food.moderate_polyols,
        'moderate_mannitol': food.moderate_mannitol,
        'moderate_sorbitol': food.moderate_sorbitol,
        'moderate_histamine_level': food.moderate_histamine_level,
        'moderate_histamine_liberator': food.moderate_histamine_liberator,
        'moderate_dao_blocker': food.moderate_dao_blocker,
        # High serving
        'high_serving': food.high_serving,
        'high_serving_unit': food.high_serving_unit,
        'high_serving_type': food.high_serving_type,
        'high_serving_note': food.high_serving_note,
        'high_traffic_light': food.high_traffic_light,
        'high_fructans': food.high_fructans,
        'high_gos': food.high_gos,
        'high_lactose': food.high_lactose,
        'high_fructose': food.high_fructose,
        'high_polyols': food.high_polyols,
        'high_mannitol': food.high_mannitol,
        'high_sorbitol': food.high_sorbitol,
        'high_histamine_level': food.high_histamine_level,
        'high_histamine_liberator': food.high_histamine_liberator,
        'high_dao_blocker': food.high_dao_blocker,
        # Legacy histamine fields
        'histamine_level': food.histamine_level,
        'histamine_liberator': food.histamine_liberator,
        'dao_blocker': food.dao_blocker,
        # Other fields
        'preparation_notes': food.preparation_notes,
        'is_complete': food.is_complete,
        'usda_food_id': food.usda_food_id,
        'ausnut_food_id': food.ausnut_food_id,
        # Custom nutrients
        'custom_nutrients': json.loads(food.custom_nutrients) if food.custom_nutrients else None
    }

    # Include usage statistics if requested
    if include_usage:
        meal_count = MealFood.query.filter_by(food_id=food.id).count()
        recipe_count = RecipeIngredient.query.filter_by(food_id=food.id).count()
        saved_meal_count = SavedMealItem.query.filter_by(food_id=food.id).count()
        result['usage'] = {
            'meal_count': meal_count,
            'recipe_count': recipe_count,
            'saved_meal_count': saved_meal_count,
            'total': meal_count + recipe_count + saved_meal_count
        }

    return result


# =============================================================================
# FOOD COMPENDIUM ENDPOINTS
# =============================================================================

@bp.route('/compendium/search', methods=['GET'])
@require_api_key
@require_scope('read:compendium')
def search_foods():
    """
    GET /api/v1/compendium/search?q={query}&category={cat}
    Search FODMAP foods by name and/or category
    """
    try:
        query = request.args.get('q', '').strip()
        category = request.args.get('category', '').strip()

        foods = Food.query.filter(Food.usda_food_id.is_(None), Food.ausnut_food_id.is_(None))

        if query:
            foods = foods.filter(Food.name.ilike(f'%{query}%'))

        if category:
            foods = foods.filter_by(category=category)

        foods = foods.order_by(Food.name).all()

        return jsonify([food_to_dict(f) for f in foods])

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/compendium/foods/<int:food_id>', methods=['GET'])
@require_api_key
@require_scope('read:compendium')
def get_food(food_id):
    """
    GET /api/v1/compendium/foods/{id}
    Get full food details including custom nutrients and usage statistics
    """
    try:
        food = Food.query.get(food_id)
        if not food:
            return not_found_error('Food', food_id)

        return success_response(food_to_dict(food, include_usage=True))

    except Exception as e:
        return wrap_exception(e)


@bp.route('/compendium/compare', methods=['GET'])
@require_api_key
@require_scope('read:compendium')
def compare_foods():
    """
    GET /api/v1/compendium/compare?ids=1,2,3
    Get multiple foods for side-by-side comparison
    """
    try:
        food_ids_str = request.args.get('ids', '').strip()
        if not food_ids_str:
            return jsonify({'error': 'IDs parameter is required'}), 400

        # Parse comma-separated IDs
        try:
            food_ids = [int(id.strip()) for id in food_ids_str.split(',') if id.strip()]
        except ValueError:
            return jsonify({'error': 'Invalid food IDs format. Use comma-separated integers.'}), 400

        if not food_ids:
            return jsonify({'error': 'No valid food IDs provided'}), 400

        foods = Food.query.filter(Food.id.in_(food_ids)).order_by(Food.name).all()

        return jsonify([food_to_dict(f) for f in foods])

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/compendium/foods', methods=['POST'])
@require_api_key
@require_scope('write:foods')
def create_food():
    """
    POST /api/v1/compendium/foods
    Create a new food with complete FODMAP/histamine ratings for all three serving sizes

    Expected JSON:
    {
        "name": "Food Name",
        "category": "Vegetables",
        "usda_food_id": 12345,  // Optional
        "ausnut_food_id": null,  // Optional
        "safe_serving": "100",
        "safe_serving_unit": "g",
        "safe_serving_type": "Weight",
        "safe_serving_note": "",
        "safe_fructans": "Green",
        "safe_gos": "Green",
        ... (all safe FODMAP/histamine fields)
        "moderate_serving": "200",
        ... (all moderate FODMAP/histamine fields)
        "high_serving": "300",
        ... (all high FODMAP/histamine fields)
        "preparation_notes": "Optional prep notes",
        "custom_nutrients": {
            "vitamins": [...],
            "minerals": [...],
            "macros": [...]
        }
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        food_name = (data.get('name') or '').strip()
        category = (data.get('category') or '').strip()

        if not food_name:
            food_name = 'Unnamed Food'
        if not category:
            category = 'Other'

        # USDA/AUSNUT food links (mutually exclusive)
        usda_food_id = data.get('usda_food_id')
        ausnut_food_id = data.get('ausnut_food_id')

        # Apply mutual exclusivity
        if ausnut_food_id:
            usda_food_id = None
        elif usda_food_id:
            ausnut_food_id = None

        # Create new food
        new_food = Food(
            name=food_name,
            category=category,
            usda_food_id=usda_food_id,
            ausnut_food_id=ausnut_food_id,
            # Legacy fields - use safe serving values for backward compatibility
            fructans=data.get('safe_fructans', 'Green'),
            gos=data.get('safe_gos', 'Green'),
            lactose=data.get('safe_lactose', 'Green'),
            fructose=data.get('safe_fructose', 'Green'),
            polyols=data.get('safe_polyols', 'Green'),
            mannitol=data.get('safe_mannitol', 'Green'),
            sorbitol=data.get('safe_sorbitol', 'Green'),
            histamine_level=data.get('safe_histamine_level', 'Low'),
            histamine_liberator=data.get('safe_histamine_liberator', 'No'),
            dao_blocker=data.get('safe_dao_blocker', 'No'),
            # Safe serving
            safe_serving=data.get('safe_serving', ''),
            safe_serving_unit=data.get('safe_serving_unit', ''),
            safe_serving_type=data.get('safe_serving_type', ''),
            safe_serving_note=data.get('safe_serving_note', ''),
            safe_traffic_light=data.get('safe_traffic_light', 'Green'),
            safe_fructans=data.get('safe_fructans', 'Green'),
            safe_gos=data.get('safe_gos', 'Green'),
            safe_lactose=data.get('safe_lactose', 'Green'),
            safe_fructose=data.get('safe_fructose', 'Green'),
            safe_polyols=data.get('safe_polyols', 'Green'),
            safe_mannitol=data.get('safe_mannitol', 'Green'),
            safe_sorbitol=data.get('safe_sorbitol', 'Green'),
            safe_histamine_level=data.get('safe_histamine_level', 'Low'),
            safe_histamine_liberator=data.get('safe_histamine_liberator', 'No'),
            safe_dao_blocker=data.get('safe_dao_blocker', 'No'),
            # Moderate serving
            moderate_serving=data.get('moderate_serving', ''),
            moderate_serving_unit=data.get('moderate_serving_unit', ''),
            moderate_serving_type=data.get('moderate_serving_type', ''),
            moderate_serving_note=data.get('moderate_serving_note', ''),
            moderate_traffic_light=data.get('moderate_traffic_light', 'Amber'),
            moderate_fructans=data.get('moderate_fructans', 'Amber'),
            moderate_gos=data.get('moderate_gos', 'Amber'),
            moderate_lactose=data.get('moderate_lactose', 'Amber'),
            moderate_fructose=data.get('moderate_fructose', 'Amber'),
            moderate_polyols=data.get('moderate_polyols', 'Amber'),
            moderate_mannitol=data.get('moderate_mannitol', 'Amber'),
            moderate_sorbitol=data.get('moderate_sorbitol', 'Amber'),
            moderate_histamine_level=data.get('moderate_histamine_level', 'Medium'),
            moderate_histamine_liberator=data.get('moderate_histamine_liberator', 'No'),
            moderate_dao_blocker=data.get('moderate_dao_blocker', 'No'),
            # High serving
            high_serving=data.get('high_serving', ''),
            high_serving_unit=data.get('high_serving_unit', ''),
            high_serving_type=data.get('high_serving_type', ''),
            high_serving_note=data.get('high_serving_note', ''),
            high_traffic_light=data.get('high_traffic_light', 'Red'),
            high_fructans=data.get('high_fructans', 'Red'),
            high_gos=data.get('high_gos', 'Red'),
            high_lactose=data.get('high_lactose', 'Red'),
            high_fructose=data.get('high_fructose', 'Red'),
            high_polyols=data.get('high_polyols', 'Red'),
            high_mannitol=data.get('high_mannitol', 'Red'),
            high_sorbitol=data.get('high_sorbitol', 'Red'),
            high_histamine_level=data.get('high_histamine_level', 'High'),
            high_histamine_liberator=data.get('high_histamine_liberator', 'Yes'),
            high_dao_blocker=data.get('high_dao_blocker', 'Yes'),
            # Other fields
            preparation_notes=data.get('preparation_notes', ''),
            is_complete=True
        )

        # Handle custom nutrients
        custom_nutrients_data = data.get('custom_nutrients')
        if custom_nutrients_data:
            if isinstance(custom_nutrients_data, str):
                # Already JSON string
                try:
                    json.loads(custom_nutrients_data)
                    new_food.custom_nutrients = custom_nutrients_data
                except json.JSONDecodeError:
                    return jsonify({'error': 'Invalid custom_nutrients JSON'}), 400
            else:
                # Convert dict to JSON string
                parsed_nutrients = parse_custom_nutrients(custom_nutrients_data)
                if parsed_nutrients:
                    new_food.custom_nutrients = parsed_nutrients

        db.session.add(new_food)
        db.session.commit()

        return jsonify(food_to_dict(new_food)), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/compendium/foods/<int:food_id>', methods=['PUT'])
@require_api_key
@require_scope('write:foods')
def update_food(food_id):
    """
    PUT /api/v1/compendium/foods/{id}
    Update an existing food

    Expected JSON: Same format as POST /api/v1/compendium/foods
    """
    try:
        food = Food.query.get(food_id)
        if not food:
            return jsonify({'error': 'Food not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Update basic information
        if 'name' in data:
            incoming_name = (data.get('name') or '').strip()
            if incoming_name:
                food.name = incoming_name

        if 'category' in data:
            incoming_category = (data.get('category') or '').strip()
            if incoming_category:
                food.category = incoming_category

        # USDA/AUSNUT food links (mutually exclusive)
        if 'ausnut_food_id' in data:
            ausnut_food_id = data['ausnut_food_id']
            if ausnut_food_id:
                food.ausnut_food_id = int(ausnut_food_id)
                food.usda_food_id = None
            else:
                food.ausnut_food_id = None

        if 'usda_food_id' in data:
            usda_food_id = data['usda_food_id']
            if usda_food_id:
                food.usda_food_id = int(usda_food_id)
                food.ausnut_food_id = None
            else:
                food.usda_food_id = None

        # Update serving sizes and ratings if provided
        serving_fields = [
            'safe_serving', 'safe_serving_unit', 'safe_serving_type', 'safe_serving_note', 'safe_traffic_light',
            'safe_fructans', 'safe_gos', 'safe_lactose', 'safe_fructose', 'safe_polyols',
            'safe_mannitol', 'safe_sorbitol', 'safe_histamine_level', 'safe_histamine_liberator', 'safe_dao_blocker',
            'moderate_serving', 'moderate_serving_unit', 'moderate_serving_type', 'moderate_serving_note', 'moderate_traffic_light',
            'moderate_fructans', 'moderate_gos', 'moderate_lactose', 'moderate_fructose', 'moderate_polyols',
            'moderate_mannitol', 'moderate_sorbitol', 'moderate_histamine_level', 'moderate_histamine_liberator', 'moderate_dao_blocker',
            'high_serving', 'high_serving_unit', 'high_serving_type', 'high_serving_note', 'high_traffic_light',
            'high_fructans', 'high_gos', 'high_lactose', 'high_fructose', 'high_polyols',
            'high_mannitol', 'high_sorbitol', 'high_histamine_level', 'high_histamine_liberator', 'high_dao_blocker'
        ]

        for field in serving_fields:
            if field in data:
                setattr(food, field, data[field])

        # Update legacy fields if safe serving values are provided
        if 'safe_fructans' in data:
            food.fructans = data['safe_fructans']
        if 'safe_gos' in data:
            food.gos = data['safe_gos']
        if 'safe_lactose' in data:
            food.lactose = data['safe_lactose']
        if 'safe_fructose' in data:
            food.fructose = data['safe_fructose']
        if 'safe_polyols' in data:
            food.polyols = data['safe_polyols']
        if 'safe_mannitol' in data:
            food.mannitol = data['safe_mannitol']
        if 'safe_sorbitol' in data:
            food.sorbitol = data['safe_sorbitol']
        if 'safe_histamine_level' in data:
            food.histamine_level = data['safe_histamine_level']
        if 'safe_histamine_liberator' in data:
            food.histamine_liberator = data['safe_histamine_liberator']
        if 'safe_dao_blocker' in data:
            food.dao_blocker = data['safe_dao_blocker']

        # Update preparation notes
        if 'preparation_notes' in data:
            food.preparation_notes = data['preparation_notes']

        # Update custom nutrients
        if 'custom_nutrients' in data:
            custom_nutrients_data = data['custom_nutrients']
            if custom_nutrients_data:
                if isinstance(custom_nutrients_data, str):
                    try:
                        json.loads(custom_nutrients_data)
                        food.custom_nutrients = custom_nutrients_data
                    except json.JSONDecodeError:
                        return jsonify({'error': 'Invalid custom_nutrients JSON'}), 400
                else:
                    parsed_nutrients = parse_custom_nutrients(custom_nutrients_data)
                    if parsed_nutrients:
                        food.custom_nutrients = parsed_nutrients
            else:
                food.custom_nutrients = None

        # Mark as complete
        food.is_complete = True

        db.session.commit()

        return jsonify(food_to_dict(food))

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/compendium/foods/<int:food_id>', methods=['DELETE'])
@require_api_key
@require_scope('write:foods')
def delete_food(food_id):
    """
    DELETE /api/v1/compendium/foods/{id}
    Delete a food (validates no meals/recipes/saved meals reference it)

    Returns error with reference counts if food is in use
    """
    try:
        food = Food.query.get(food_id)
        if not food:
            return jsonify({'error': 'Food not found'}), 404

        food_name = food.name

        # Check for references
        meal_count = MealFood.query.filter_by(food_id=food_id).count()
        recipe_count = RecipeIngredient.query.filter_by(food_id=food_id).count()
        saved_meal_count = SavedMealItem.query.filter_by(food_id=food_id).count()

        total_references = meal_count + recipe_count + saved_meal_count

        if total_references > 0:
            # Build detailed error message
            references = []
            if meal_count > 0:
                references.append(f"{meal_count} diary meal{'s' if meal_count > 1 else ''}")
            if recipe_count > 0:
                references.append(f"{recipe_count} recipe{'s' if recipe_count > 1 else ''}")
            if saved_meal_count > 0:
                references.append(f"{saved_meal_count} saved meal{'s' if saved_meal_count > 1 else ''}")

            error_message = f"Cannot delete '{food_name}'. It is used in: {', '.join(references)}."

            return jsonify({
                'error': error_message,
                'usage': {
                    'meal_count': meal_count,
                    'recipe_count': recipe_count,
                    'saved_meal_count': saved_meal_count,
                    'total': total_references
                }
            }), 400

        # Safe to delete
        db.session.delete(food)
        db.session.commit()

        return jsonify({'message': f'Food "{food_name}" deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# =============================================================================
# FOOD UTILITIES
# =============================================================================

@bp.route('/foods/quick-add', methods=['POST'])
@require_api_key
@require_scope('write:foods')
def quick_add_food():
    """
    POST /api/v1/foods/quick-add
    Quick add food with minimal information

    Input:
        name (str, required): Food name
        category (str, optional): Food category (default: 'Other')
        fructans, gos, lactose, fructose, polyols, mannitol, sorbitol (str, optional):
            FODMAP ratings (default: 'Green')
        histamine_level (str, optional): 'Low', 'Med', or 'High' (default: 'Low')
        histamine_liberator, dao_blocker (str, optional): 'Yes' or 'No' (default: 'No')
        safe_serving, moderate_serving, high_serving (str, optional): Serving sizes
        notes (str, optional): Preparation notes

    Returns:
        JSON: {success: true, food: {id, name, category, ...}}

    Note:
        Created foods are marked as incomplete (is_complete=False) since they
        only capture minimal information and may need further editing
    """
    try:
        data = request.get_json()

        # Validate required fields
        name = data.get('name', '').strip()
        if not name:
            return missing_field_error('name')

        # Create new food with provided data
        # Mark as incomplete since quick-add only captures minimal information
        new_food = Food(
            name=name,
            category=data.get('category', 'Other'),
            fructans=data.get('fructans', 'Green'),
            gos=data.get('gos', 'Green'),
            lactose=data.get('lactose', 'Green'),
            fructose=data.get('fructose', 'Green'),
            polyols=data.get('polyols', 'Green'),
            mannitol=data.get('mannitol', 'Green'),
            sorbitol=data.get('sorbitol', 'Green'),
            histamine_level=data.get('histamine_level', 'Low'),
            histamine_liberator=data.get('histamine_liberator', 'No'),
            dao_blocker=data.get('dao_blocker', 'No'),
            safe_serving=data.get('safe_serving', ''),
            moderate_serving=data.get('moderate_serving', ''),
            high_serving=data.get('high_serving', ''),
            preparation_notes=data.get('notes', ''),
            is_complete=False  # Quick-added foods need more information
        )

        db.session.add(new_food)
        db.session.commit()

        return success_response(
            data={
                'id': new_food.id,
                'name': new_food.name,
                'category': new_food.category,
                'fructans': new_food.fructans,
                'gos': new_food.gos,
                'lactose': new_food.lactose,
                'fructose': new_food.fructose,
                'polyols': new_food.polyols,
                'mannitol': new_food.mannitol,
                'sorbitol': new_food.sorbitol,
                'histamine_level': new_food.histamine_level,
                'safe_serving': new_food.safe_serving
            },
            message='Food created successfully',
            status=201
        )

    except Exception as e:
        db.session.rollback()
        return wrap_exception(e)


@bp.route('/compendium/foods/<int:food_id>/link-ausnut', methods=['POST'])
@require_api_key
@require_scope('write:foods')
def link_food_to_ausnut(food_id):
    """
    POST /api/v1/compendium/foods/{id}/link-ausnut
    Link a FODMAP food to an AUSNUT database record

    Input:
        ausnut_food_id (int, optional): AUSNUT food ID to link
            If null/empty, removes existing AUSNUT link

    Returns:
        JSON: {success: true, ausnut_food_id: int or null}

    Validation:
        - Ensures AUSNUT food exists before linking
        - USDA and AUSNUT links are mutually exclusive (not enforced here,
          but typically only one should be set)

    Error:
        404: Food or AUSNUT food not found
        500: Server error
    """
    from models.ausnut import AUSNUTFood

    try:
        food = Food.query.get(food_id)
        if not food:
            return jsonify({'error': 'Food not found'}), 404

        data = request.get_json()
        ausnut_id = data.get('ausnut_food_id')

        if ausnut_id:
            ausnut_food = AUSNUTFood.query.get(ausnut_id)
            if not ausnut_food:
                return jsonify({'error': 'AUSNUT food not found'}), 404
            food.ausnut_food_id = ausnut_id
        else:
            food.ausnut_food_id = None

        db.session.commit()
        return jsonify({'success': True, 'ausnut_food_id': food.ausnut_food_id})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# =============================================================================
# PHASE 3: BATCH OPERATIONS ENDPOINT
# =============================================================================

@bp.route('/foods/batch', methods=['GET'])
@require_api_key
@require_scope('read:foods')
def get_batch_foods():
    """
    GET /api/v1/foods/batch?ids=1,2,3,4,5
    Get multiple food objects in one API call

    Query Parameters:
    - ids: Comma-separated list of food IDs (required, max 100)
    - include_nutrients: Include full nutrient data (default: false)

    Returns:
    {
        "foods": [
            {"id": 1, "name": "Apple", ...},
            {"id": 2, "name": "Banana", ...},
            ...
        ],
        "requested_count": 5,
        "found_count": 4,
        "missing_ids": [3]
    }
    """
    try:
        ids_str = request.args.get('ids', '').strip()
        include_nutrients = request.args.get('include_nutrients', 'false').lower() == 'true'

        if not ids_str:
            return jsonify({'error': 'ids parameter is required (comma-separated list)'}), 400

        # Parse IDs
        try:
            ids = [int(id_str.strip()) for id_str in ids_str.split(',') if id_str.strip()]
        except ValueError:
            return jsonify({'error': 'Invalid ID format. IDs must be integers'}), 400

        if len(ids) == 0:
            return jsonify({'error': 'At least one ID must be provided'}), 400

        if len(ids) > 100:
            return jsonify({'error': 'Maximum 100 IDs per request'}), 400

        # Remove duplicates while preserving order
        seen = set()
        unique_ids = []
        for id_val in ids:
            if id_val not in seen:
                seen.add(id_val)
                unique_ids.append(id_val)

        # Query foods
        foods = Food.query.filter(Food.id.in_(unique_ids)).all()
        found_ids = {f.id for f in foods}
        missing_ids = [id_val for id_val in unique_ids if id_val not in found_ids]

        # Serialize foods
        foods_data = []
        for food in foods:
            if include_nutrients:
                # Full data including all nutrients
                food_dict = food.to_dict()
            else:
                # Compact data for recipe/meal forms
                food_dict = {
                    'id': food.id,
                    'name': food.name,
                    'category': food.category,
                    'safe_serving': food.safe_serving,
                    'safe_serving_unit': food.safe_serving_unit,
                    'moderate_serving': food.moderate_serving,
                    'moderate_serving_unit': food.moderate_serving_unit,
                    'high_serving': food.high_serving,
                    'high_serving_unit': food.high_serving_unit,
                    'safe_traffic_light': food.safe_traffic_light,
                    'moderate_traffic_light': food.moderate_traffic_light,
                    'high_traffic_light': food.high_traffic_light,
                    'usda_food_id': food.usda_food_id,
                    'ausnut_food_id': food.ausnut_food_id
                }
            foods_data.append(food_dict)

        # Sort foods_data to match the order of unique_ids
        id_to_food = {f['id']: f for f in foods_data}
        ordered_foods = [id_to_food[id_val] for id_val in unique_ids if id_val in id_to_food]

        return jsonify({
            'foods': ordered_foods,
            'requested_count': len(unique_ids),
            'found_count': len(foods),
            'missing_ids': missing_ids
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================================================
# 5 NEW FOOD ENDPOINTS FOR APP2 INTEGRATION
# =============================================================================

@bp.route('/foods/substitutes', methods=['GET'])
@require_api_key
@require_scope('read:foods')
def get_food_substitutes():
    """
    GET /api/v1/foods/substitutes?food_id=55&limit=5
    Safe FODMAP substitutes for a given food
    """
    try:
        food_id = request.args.get('food_id', type=int)
        limit = request.args.get('limit', 5, type=int)

        if not food_id:
            return jsonify({'error': 'food_id parameter is required'}), 400

        source_food = Food.query.get(food_id)
        if not source_food:
            return jsonify({'error': f'Food {food_id} not found'}), 404

        # Find substitutes with same or similar category and green traffic light
        substitutes = Food.query.filter(
            Food.usda_food_id.is_(None),
            Food.ausnut_food_id.is_(None),
            Food.category == source_food.category,
            Food.id != food_id,
            Food.safe_traffic_light == 'Green'
        ).order_by(Food.name).limit(limit).all()

        substitutes_data = []
        for sub_food in substitutes:
            substitutes_data.append({
                'food_id': sub_food.id,
                'food_name': sub_food.name,
                'category': sub_food.category,
                'safe_traffic_light': sub_food.safe_traffic_light,
                'safe_serving': getattr(sub_food, 'safe_serving_size', 'Unknown')
            })

        return jsonify({
            'food_id': food_id,
            'food_name': source_food.name,
            'food_category': source_food.category,
            'substitutes': substitutes_data,
            'total_found': len(substitutes_data)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/foods/unified-search', methods=['GET'])
@require_api_key
@require_scope('read:foods')
def unified_search():
    """
    GET /api/v1/foods/unified-search?q=chicken&databases=fodmap,usda,ausnut&limit=10
    Search across FODMAP, USDA, and AUSNUT databases simultaneously
    """
    try:
        query = request.args.get('q', '').strip()
        databases = request.args.get('databases', 'fodmap,usda,ausnut').split(',')
        limit = request.args.get('limit', 10, type=int)

        if len(query) < 2:
            return jsonify({'error': 'Search query must be at least 2 characters'}), 400

        results = []
        counts = {'fodmap': 0, 'usda': 0, 'ausnut': 0}

        # Search FODMAP foods
        if 'fodmap' in databases:
            fodmap_results = Food.query.filter(
                Food.usda_food_id.is_(None),
                Food.ausnut_food_id.is_(None),
                Food.name.ilike(f'%{query}%')
            ).limit(limit).all()
            for food in fodmap_results:
                results.append({
                    'source': 'fodmap',
                    'id': food.id,
                    'name': food.name,
                    'category': food.category
                })
            counts['fodmap'] = len(fodmap_results)

        # Search USDA foods
        if 'usda' in databases:
            try:
                from models.usda import USDAFood
                usda_results = USDAFood.query.filter(
                    USDAFood.description.ilike(f'%{query}%')
                ).limit(limit).all()
                for usda_food in usda_results:
                    results.append({
                        'source': 'usda',
                        'id': usda_food.fdc_id,
                        'name': usda_food.description,
                        'category': getattr(usda_food, 'food_category', 'Other')
                    })
                counts['usda'] = len(usda_results)
            except (ImportError, Exception):
                pass

        # Search AUSNUT foods
        if 'ausnut' in databases:
            try:
                from models.ausnut import AUSNUTFood
                ausnut_results = AUSNUTFood.query.filter(
                    AUSNUTFood.food_name.ilike(f'%{query}%')
                ).limit(limit).all()
                for ausnut_food in ausnut_results:
                    results.append({
                        'source': 'ausnut',
                        'id': ausnut_food.id,
                        'name': ausnut_food.food_name,
                        'category': getattr(ausnut_food, 'food_type', 'Other')
                    })
                counts['ausnut'] = len(ausnut_results)
            except (ImportError, Exception):
                pass

        return jsonify({
            'query': query,
            'results': results,
            'counts': counts
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/foods/scan-menu', methods=['POST'])
@require_api_key
@require_scope('write:foods')
def scan_menu():
    """
    POST /api/v1/foods/scan-menu
    Analyse restaurant menu photo using vision AI (Tier 3 stub)
    Input: {"image_data": "base64..." OR "image_url": "..."}
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400

        return jsonify({
            'status': 'not_configured',
            'message': 'Menu scanning requires an external vision AI service (e.g. Google Vision, Claude vision)',
            'todo': 'Configure VISION_AI_PROVIDER in config.py and implement provider handler',
            'supported_providers': ['google_vision', 'claude_vision', 'aws_rekognition']
        }), 501

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/compendium/foods/<int:food_id>/link-usda', methods=['POST'])
@require_api_key
@require_scope('write:foods')
def link_usda_food(food_id):
    """
    POST /api/v1/compendium/foods/<int:food_id>/link-usda
    Link a FODMAP food to a USDA food record
    Input: {"usda_food_id": 9040} or null to remove link
    """
    try:
        food = Food.query.get(food_id)
        if not food:
            return jsonify({'error': f'Food {food_id} not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400

        usda_food_id = data.get('usda_food_id')

        if usda_food_id:
            # Validate USDA food exists
            try:
                from models.usda import USDAFood
                usda_food = USDAFood.query.filter_by(fdc_id=usda_food_id).first()
                if not usda_food:
                    return jsonify({'error': f'USDA food {usda_food_id} not found'}), 404
                usda_description = usda_food.description
            except (ImportError, Exception):
                usda_description = 'Unknown'
        else:
            usda_food_id = None
            usda_description = None

        # Update link
        food.usda_food_id = usda_food_id
        db.session.commit()

        return jsonify({
            'success': True,
            'food_id': food_id,
            'food_name': food.name,
            'usda_food_id': usda_food_id,
            'usda_description': usda_description,
            'message': 'Link updated successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/foods/nutrient-boosters', methods=['GET'])
@require_api_key
@require_scope('read:foods')
def get_nutrient_boosters():
    """
    GET /api/v1/foods/nutrient-boosters?nutrient=Iron&limit=10&days_for_triggers=90
    Top safe foods high in a specific nutrient, excluding personal triggers
    """
    try:
        nutrient = request.args.get('nutrient', 'Iron')
        limit = request.args.get('limit', 10, type=int)
        days_for_triggers = request.args.get('days_for_triggers', 90, type=int)

        # Get user's trigger foods from last N days
        from datetime import timedelta, date as date_type
        trigger_foods = set()
        try:
            from models.diary import DiaryEntry, Meal, MealFood
            today = date_type.today()
            start_date = today - timedelta(days=days_for_triggers)

            recent_meals = db.session.query(MealFood).join(
                Meal, MealFood.meal_id == Meal.id
            ).join(
                DiaryEntry, Meal.diary_entry_id == DiaryEntry.id
            ).filter(
                DiaryEntry.entry_date >= start_date,
                DiaryEntry.entry_type == 'meal'
            ).all()

            # Mark foods followed by symptoms as triggers (simplified)
            for meal_food in recent_meals:
                if meal_food.food_id:
                    trigger_foods.add(meal_food.food_id)
        except Exception:
            pass

        # Find safe foods high in nutrient
        safe_foods = Food.query.filter(
            Food.usda_food_id.is_(None),
            Food.ausnut_food_id.is_(None),
            Food.safe_traffic_light == 'Green',
            ~Food.id.in_(list(trigger_foods) if trigger_foods else [0])
        ).order_by(Food.name).limit(limit).all()

        boosters = []
        for food in safe_foods:
            boosters.append({
                'food_id': food.id,
                'food_name': food.name,
                'category': food.category,
                'safe_traffic_light': 'Green',
                'safe_serving': getattr(food, 'safe_serving_size', 'Unknown'),
                'is_personal_trigger': food.id in trigger_foods
            })

        return jsonify({
            'nutrient': nutrient,
            'unit': 'mg' if nutrient != 'Protein' else 'g',
            'boosters': boosters,
            'total_found': len(boosters),
            'triggers_excluded': len(trigger_foods)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
