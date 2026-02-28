from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from models.food import Food
from models.diary import MealFood
from models.recipe import RecipeIngredient, SavedMealItem
from database import db
import json

bp = Blueprint('compendium', __name__, url_prefix='/compendium')


def parse_custom_nutrients(form):
    """Parse custom nutrients from form data and return as JSON string"""
    def safe_value(value):
        """Safely parse a nutrient value, preserving symbols like <, >, ~ before numbers.
        Returns float for pure numbers, string for values with symbols, None for empty."""
        if value is None or value == '':
            return None
        value = value.strip()
        if not value:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            # Keep the original string (e.g. "<0.1", "~5", ">10")
            return value

    custom_nutrients = {
        'vitamins': [],
        'minerals': [],
        'macros': []
    }

    # Parse custom vitamins
    i = 1
    while True:
        name = form.get(f'custom_vitamin_name_{i}')
        if not name:
            break
        custom_nutrients['vitamins'].append({
            'name': name.strip(),
            'per_serve': safe_value(form.get(f'custom_vitamin_per_serve_{i}')),
            'per_100': safe_value(form.get(f'custom_vitamin_per_100_{i}')),
            'unit': form.get(f'custom_vitamin_unit_{i}', 'mg'),
            'rdi': form.get(f'custom_vitamin_rdi_{i}', '').strip(),
            'order': i
        })
        i += 1

    # Parse custom minerals
    i = 1
    while True:
        name = form.get(f'custom_mineral_name_{i}')
        if not name:
            break
        custom_nutrients['minerals'].append({
            'name': name.strip(),
            'per_serve': safe_value(form.get(f'custom_mineral_per_serve_{i}')),
            'per_100': safe_value(form.get(f'custom_mineral_per_100_{i}')),
            'unit': 'mg',
            'rdi': form.get(f'custom_mineral_rdi_{i}', '').strip(),
            'order': i
        })
        i += 1

    # Parse custom macronutrients
    i = 1
    while True:
        name = form.get(f'custom_macro_name_{i}')
        if not name:
            break
        custom_nutrients['macros'].append({
            'name': name.strip(),
            'per_serve': safe_value(form.get(f'custom_macro_per_serve_{i}')),
            'per_100': safe_value(form.get(f'custom_macro_per_100_{i}')),
            'unit': 'g',
            'order': i
        })
        i += 1

    # Only return JSON if there are any custom nutrients
    if custom_nutrients['vitamins'] or custom_nutrients['minerals'] or custom_nutrients['macros']:
        return json.dumps(custom_nutrients)
    return None

@bp.route('/cache-test')
def cache_test():
    """Cache test page to verify fresh content"""
    from datetime import datetime
    return render_template('cache_test.html', timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@bp.route('/')
def index():
    """Food guide home page - includes FODMAP database and USDA nutrition data"""
    # Import USDA models for the merged page
    try:
        from models.usda import USDAFood, USDAFoodCategory

        # Get USDA categories with food counts
        usda_categories = USDAFoodCategory.query.filter(
            USDAFoodCategory.food_count > 0
        ).order_by(USDAFoodCategory.description).all()

        # Get USDA food counts by data type
        usda_total = USDAFood.query.count()
        foundation_count = USDAFood.query.filter_by(data_type='Foundation').count()
        sr_legacy_count = USDAFood.query.filter_by(data_type='SR Legacy').count()
        survey_count = USDAFood.query.filter_by(data_type='Survey').count()
        branded_count = USDAFood.query.filter_by(data_type='Branded').count()
    except Exception:
        # USDA tables may not exist yet
        usda_categories = []
        usda_total = 0
        foundation_count = 0
        sr_legacy_count = 0
        survey_count = 0
        branded_count = 0

    # Import AUSNUT data for the merged page
    try:
        from models.ausnut import AUSNUTFood
        ausnut_total = AUSNUTFood.query.count()
    except Exception:
        ausnut_total = 0

    return render_template(
        'compendium/index.html',
        usda_categories=usda_categories,
        usda_total=usda_total,
        foundation_count=foundation_count,
        sr_legacy_count=sr_legacy_count,
        survey_count=survey_count,
        branded_count=branded_count,
        ausnut_total=ausnut_total
    )

@bp.route('/search')
def search():
    """Food search interface"""
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    view_all = request.args.get('view_all', '')

    foods = Food.query.filter(Food.usda_food_id.is_(None), Food.ausnut_food_id.is_(None))

    if query:
        foods = foods.filter(Food.name.ilike(f'%{query}%'))

    if category:
        foods = foods.filter_by(category=category)

    foods = foods.order_by(Food.name).all()

    return render_template('compendium/search.html',
                         foods=foods,
                         query=query,
                         category=category,
                         view_all=view_all)

@bp.route('/<int:food_id>')
def detail(food_id):
    """Individual food detail page"""
    food = Food.query.get_or_404(food_id)

    # Calculate usage counts
    meal_count = MealFood.query.filter_by(food_id=food_id).count()
    recipe_ingredients = RecipeIngredient.query.filter_by(food_id=food_id).all()
    recipe_count = len(recipe_ingredients)
    recipes_using_food = [ri.recipe for ri in recipe_ingredients]
    saved_meal_count = SavedMealItem.query.filter_by(food_id=food_id).count()

    # Parse custom nutrients JSON for template
    custom_nutrients = None
    if food.custom_nutrients:
        try:
            custom_nutrients = json.loads(food.custom_nutrients)
        except (json.JSONDecodeError, TypeError):
            custom_nutrients = None

    return render_template('compendium/detail.html',
                         food=food,
                         custom_nutrients=custom_nutrients,
                         meal_count=meal_count,
                         recipe_count=recipe_count,
                         recipes_using_food=recipes_using_food,
                         saved_meal_count=saved_meal_count)

@bp.route('/compare')
def compare():
    """Compare multiple foods"""
    food_ids = request.args.getlist('ids')
    foods = Food.query.filter(Food.id.in_(food_ids)).order_by(Food.name).all() if food_ids else []
    return render_template('compendium/compare.html', foods=foods)

@bp.route('/api/usda-search')
def usda_search_api():
    """API endpoint for searching USDA foods"""
    try:
        from models.usda import USDAFood

        query = request.args.get('q', '').strip()
        if not query or len(query) < 2:
            return jsonify({'foods': []})

        # Search USDA foods by description
        foods = USDAFood.query.filter(
            USDAFood.description.ilike(f'%{query}%')
        ).order_by(USDAFood.description).limit(50).all()

        # Convert to JSON
        results = [{
            'id': food.id,
            'fdc_id': food.fdc_id,
            'description': food.description,
            'data_type': food.data_type,
            'category': food.category.description if food.category else None
        } for food in foods]

        return jsonify({'foods': results})
    except Exception as e:
        return jsonify({'error': str(e), 'foods': []})

@bp.route('/api/usda-food/<int:food_id>')
def usda_food_detail_api(food_id):
    """API endpoint for getting USDA food details"""
    try:
        from models.usda import USDAFood

        food = USDAFood.query.get_or_404(food_id)

        # Get key nutrients for preview
        nutrients = {}
        nutrient_names = ['Energy', 'Protein', 'Total lipid (fat)', 'Carbohydrate, by difference',
                         'Sugars, total including NLEA', 'Fiber, total dietary', 'Sodium, Na']

        for fn in food.nutrients:
            if fn.nutrient and fn.nutrient.name in nutrient_names:
                nutrients[fn.nutrient.name] = {
                    'amount': fn.amount,
                    'unit': fn.nutrient.unit_name
                }

        return jsonify({
            'id': food.id,
            'fdc_id': food.fdc_id,
            'description': food.description,
            'data_type': food.data_type,
            'category': food.category.description if food.category else None,
            'nutrients': nutrients
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@bp.route('/add', methods=['GET', 'POST'])
def add_food():
    """Add a custom food to the library"""
    if request.method == 'POST':
        try:
            # Get form data
            food_name = (request.form.get('food_name') or '').strip()
            category = (request.form.get('category') or '').strip()
            if not food_name:
                food_name = 'Unnamed Food'
            if not category:
                category = 'Other'

            # USDA food link
            usda_food_id = request.form.get('usda_food_id', '').strip()
            usda_food_id = int(usda_food_id) if usda_food_id else None

            # Serving sizes
            safe_serving = request.form.get('safe_serving', '')
            safe_serving_unit = request.form.get('safe_serving_unit', '')
            moderate_serving = request.form.get('moderate_serving', '')
            moderate_serving_unit = request.form.get('moderate_serving_unit', '')
            high_serving = request.form.get('high_serving', '')
            high_serving_unit = request.form.get('high_serving_unit', '')

            # Serving types and notes
            safe_serving_type = request.form.get('safe_serving_type', '')
            safe_serving_note = request.form.get('safe_serving_note', '')
            moderate_serving_type = request.form.get('moderate_serving_type', '')
            moderate_serving_note = request.form.get('moderate_serving_note', '')
            high_serving_type = request.form.get('high_serving_type', '')
            high_serving_note = request.form.get('high_serving_note', '')

            # Safe serving FODMAP ratings
            safe_fructans = request.form.get('safe_fructans', 'Green')
            safe_gos = request.form.get('safe_gos', 'Green')
            safe_lactose = request.form.get('safe_lactose', 'Green')
            safe_fructose = request.form.get('safe_fructose', 'Green')
            safe_polyols = request.form.get('safe_polyols', 'Green')
            safe_mannitol = request.form.get('safe_mannitol', 'Green')
            safe_sorbitol = request.form.get('safe_sorbitol', 'Green')

            # Moderate serving FODMAP ratings
            moderate_fructans = request.form.get('moderate_fructans', 'Amber')
            moderate_gos = request.form.get('moderate_gos', 'Amber')
            moderate_lactose = request.form.get('moderate_lactose', 'Amber')
            moderate_fructose = request.form.get('moderate_fructose', 'Amber')
            moderate_polyols = request.form.get('moderate_polyols', 'Amber')
            moderate_mannitol = request.form.get('moderate_mannitol', 'Amber')
            moderate_sorbitol = request.form.get('moderate_sorbitol', 'Amber')

            # High serving FODMAP ratings
            high_fructans = request.form.get('high_fructans', 'Red')
            high_gos = request.form.get('high_gos', 'Red')
            high_lactose = request.form.get('high_lactose', 'Red')
            high_fructose = request.form.get('high_fructose', 'Red')
            high_polyols = request.form.get('high_polyols', 'Red')
            high_mannitol = request.form.get('high_mannitol', 'Red')
            high_sorbitol = request.form.get('high_sorbitol', 'Red')

            # Safe serving histamine ratings
            safe_histamine_level = request.form.get('safe_histamine_level', 'Low')
            safe_histamine_liberator = request.form.get('safe_histamine_liberator', 'No')
            safe_dao_blocker = request.form.get('safe_dao_blocker', 'No')

            # Moderate serving histamine ratings
            moderate_histamine_level = request.form.get('moderate_histamine_level', 'Medium')
            moderate_histamine_liberator = request.form.get('moderate_histamine_liberator', 'No')
            moderate_dao_blocker = request.form.get('moderate_dao_blocker', 'No')

            # High serving histamine ratings
            high_histamine_level = request.form.get('high_histamine_level', 'High')
            high_histamine_liberator = request.form.get('high_histamine_liberator', 'Yes')
            high_dao_blocker = request.form.get('high_dao_blocker', 'Yes')

            prep_notes = request.form.get('notes', '')

            # NOTE: Nutrition fields (health_star_rating, serving_size, energy, macros, vitamins, minerals, etc.)
            # are no longer stored in the Food table. They are now read-only properties that return None.
            # Nutritional data comes from the USDA database via the usda_food relationship.
            # The form may still submit these fields, but we don't save them.

            # Create new food
            # Foods created via full form are marked as complete
            new_food = Food(
                name=food_name,
                category=category,
                # USDA food link
                usda_food_id=usda_food_id,
                # Legacy fields - use safe serving values for backward compatibility
                fructans=safe_fructans,
                gos=safe_gos,
                lactose=safe_lactose,
                fructose=safe_fructose,
                polyols=safe_polyols,
                mannitol=safe_mannitol,
                sorbitol=safe_sorbitol,
                # Safe serving FODMAP ratings
                safe_fructans=safe_fructans,
                safe_gos=safe_gos,
                safe_lactose=safe_lactose,
                safe_fructose=safe_fructose,
                safe_polyols=safe_polyols,
                safe_mannitol=safe_mannitol,
                safe_sorbitol=safe_sorbitol,
                # Moderate serving FODMAP ratings
                moderate_fructans=moderate_fructans,
                moderate_gos=moderate_gos,
                moderate_lactose=moderate_lactose,
                moderate_fructose=moderate_fructose,
                moderate_polyols=moderate_polyols,
                moderate_mannitol=moderate_mannitol,
                moderate_sorbitol=moderate_sorbitol,
                # High serving FODMAP ratings
                high_fructans=high_fructans,
                high_gos=high_gos,
                high_lactose=high_lactose,
                high_fructose=high_fructose,
                high_polyols=high_polyols,
                high_mannitol=high_mannitol,
                high_sorbitol=high_sorbitol,
                # Legacy histamine fields - use safe serving values for backward compatibility
                histamine_level=safe_histamine_level,
                histamine_liberator=safe_histamine_liberator,
                dao_blocker=safe_dao_blocker,
                # Safe serving histamine ratings
                safe_histamine_level=safe_histamine_level,
                safe_histamine_liberator=safe_histamine_liberator,
                safe_dao_blocker=safe_dao_blocker,
                # Moderate serving histamine ratings
                moderate_histamine_level=moderate_histamine_level,
                moderate_histamine_liberator=moderate_histamine_liberator,
                moderate_dao_blocker=moderate_dao_blocker,
                # High serving histamine ratings
                high_histamine_level=high_histamine_level,
                high_histamine_liberator=high_histamine_liberator,
                high_dao_blocker=high_dao_blocker,
                # Servings and notes
                safe_serving=safe_serving,
                safe_serving_unit=safe_serving_unit,
                moderate_serving=moderate_serving,
                moderate_serving_unit=moderate_serving_unit,
                high_serving=high_serving,
                high_serving_unit=high_serving_unit,
                safe_serving_type=safe_serving_type,
                safe_serving_note=safe_serving_note,
                moderate_serving_type=moderate_serving_type,
                moderate_serving_note=moderate_serving_note,
                high_serving_type=high_serving_type,
                high_serving_note=high_serving_note,
                preparation_notes=prep_notes,
                # Custom nutrients - check for new JSON format first, fall back to old parser
                custom_nutrients=None,  # Will be set below
                # Mark as complete since it was created via full form
                is_complete=True
            )

            # Handle custom nutrients - new JSON format or old parser
            custom_nutrients_json = request.form.get('custom_nutrients', '').strip()
            if custom_nutrients_json and custom_nutrients_json != '{}':
                # New format: JSON data from custom nutrition section
                try:
                    # Validate it's proper JSON
                    json.loads(custom_nutrients_json)
                    new_food.custom_nutrients = custom_nutrients_json
                except json.JSONDecodeError:
                    # Invalid JSON, try old parser
                    parsed_nutrients = parse_custom_nutrients(request.form)
                    if parsed_nutrients:
                        new_food.custom_nutrients = parsed_nutrients
            else:
                # Try old format parser for backward compatibility
                parsed_nutrients = parse_custom_nutrients(request.form)
                if parsed_nutrients:
                    new_food.custom_nutrients = parsed_nutrients

            db.session.add(new_food)
            db.session.commit()

            flash(f'"{food_name}" added successfully!', 'success')
            return redirect(url_for('compendium.detail', food_id=new_food.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error adding food: {str(e)}', 'error')
            return redirect(url_for('compendium.add_food'))

    return render_template('compendium/add-food.html')

@bp.route('/edit/<int:food_id>', methods=['GET', 'POST'])
def edit_food(food_id):
    """Edit an existing food in the library"""
    food = Food.query.get_or_404(food_id)

    if request.method == 'POST':
        try:
            # Update basic information
            incoming_name = (request.form.get('food_name') or '').strip()
            if incoming_name:
                food.name = incoming_name
            incoming_category = (request.form.get('category') or '').strip()
            if incoming_category:
                food.category = incoming_category

            # Nutritional database links (mutually exclusive)
            usda_food_id = request.form.get('usda_food_id', '').strip()
            ausnut_food_id = request.form.get('ausnut_food_id', '').strip()

            # Apply mutual exclusivity: only one nutrition source can be active
            if ausnut_food_id:
                food.ausnut_food_id = int(ausnut_food_id)
                food.usda_food_id = None  # Clear USDA if AUSNUT is set
            elif usda_food_id:
                food.usda_food_id = int(usda_food_id)
                food.ausnut_food_id = None  # Clear AUSNUT if USDA is set
            else:
                # No external database link - allow custom nutrition
                food.usda_food_id = None
                food.ausnut_food_id = None

            # Serving sizes
            food.safe_serving = request.form.get('safe_serving', '')
            food.safe_serving_unit = request.form.get('safe_serving_unit', '')
            food.moderate_serving = request.form.get('moderate_serving', '')
            food.moderate_serving_unit = request.form.get('moderate_serving_unit', '')
            food.high_serving = request.form.get('high_serving', '')
            food.high_serving_unit = request.form.get('high_serving_unit', '')

            # Serving types and notes
            food.safe_serving_type = request.form.get('safe_serving_type', '')
            food.safe_serving_note = request.form.get('safe_serving_note', '')
            food.moderate_serving_type = request.form.get('moderate_serving_type', '')
            food.moderate_serving_note = request.form.get('moderate_serving_note', '')
            food.high_serving_type = request.form.get('high_serving_type', '')
            food.high_serving_note = request.form.get('high_serving_note', '')

            # Traffic light colors
            food.safe_traffic_light = request.form.get('safe_traffic_light', 'Green')
            food.moderate_traffic_light = request.form.get('moderate_traffic_light', 'Amber')
            food.high_traffic_light = request.form.get('high_traffic_light', 'Red')

            # Safe serving FODMAP ratings
            safe_fructans = request.form.get('safe_fructans', 'Green')
            safe_gos = request.form.get('safe_gos', 'Green')
            safe_lactose = request.form.get('safe_lactose', 'Green')
            safe_fructose = request.form.get('safe_fructose', 'Green')
            safe_polyols = request.form.get('safe_polyols', 'Green')
            safe_mannitol = request.form.get('safe_mannitol', 'Green')
            safe_sorbitol = request.form.get('safe_sorbitol', 'Green')

            # Moderate serving FODMAP ratings
            moderate_fructans = request.form.get('moderate_fructans', 'Amber')
            moderate_gos = request.form.get('moderate_gos', 'Amber')
            moderate_lactose = request.form.get('moderate_lactose', 'Amber')
            moderate_fructose = request.form.get('moderate_fructose', 'Amber')
            moderate_polyols = request.form.get('moderate_polyols', 'Amber')
            moderate_mannitol = request.form.get('moderate_mannitol', 'Amber')
            moderate_sorbitol = request.form.get('moderate_sorbitol', 'Amber')

            # High serving FODMAP ratings
            high_fructans = request.form.get('high_fructans', 'Red')
            high_gos = request.form.get('high_gos', 'Red')
            high_lactose = request.form.get('high_lactose', 'Red')
            high_fructose = request.form.get('high_fructose', 'Red')
            high_polyols = request.form.get('high_polyols', 'Red')
            high_mannitol = request.form.get('high_mannitol', 'Red')
            high_sorbitol = request.form.get('high_sorbitol', 'Red')

            # Safe serving histamine ratings
            safe_histamine_level = request.form.get('safe_histamine_level', 'Low')
            safe_histamine_liberator = request.form.get('safe_histamine_liberator', 'No')
            safe_dao_blocker = request.form.get('safe_dao_blocker', 'No')

            # Moderate serving histamine ratings
            moderate_histamine_level = request.form.get('moderate_histamine_level', 'Medium')
            moderate_histamine_liberator = request.form.get('moderate_histamine_liberator', 'No')
            moderate_dao_blocker = request.form.get('moderate_dao_blocker', 'No')

            # High serving histamine ratings
            high_histamine_level = request.form.get('high_histamine_level', 'High')
            high_histamine_liberator = request.form.get('high_histamine_liberator', 'Yes')
            high_dao_blocker = request.form.get('high_dao_blocker', 'Yes')

            # Update legacy fields for backward compatibility (use safe serving values)
            food.fructans = safe_fructans
            food.gos = safe_gos
            food.lactose = safe_lactose
            food.fructose = safe_fructose
            food.polyols = safe_polyols
            food.mannitol = safe_mannitol
            food.sorbitol = safe_sorbitol
            food.histamine_level = safe_histamine_level
            food.histamine_liberator = safe_histamine_liberator
            food.dao_blocker = safe_dao_blocker

            # Update safe serving ratings
            food.safe_fructans = safe_fructans
            food.safe_gos = safe_gos
            food.safe_lactose = safe_lactose
            food.safe_fructose = safe_fructose
            food.safe_polyols = safe_polyols
            food.safe_mannitol = safe_mannitol
            food.safe_sorbitol = safe_sorbitol
            food.safe_histamine_level = safe_histamine_level
            food.safe_histamine_liberator = safe_histamine_liberator
            food.safe_dao_blocker = safe_dao_blocker

            # Update moderate serving ratings
            food.moderate_fructans = moderate_fructans
            food.moderate_gos = moderate_gos
            food.moderate_lactose = moderate_lactose
            food.moderate_fructose = moderate_fructose
            food.moderate_polyols = moderate_polyols
            food.moderate_mannitol = moderate_mannitol
            food.moderate_sorbitol = moderate_sorbitol
            food.moderate_histamine_level = moderate_histamine_level
            food.moderate_histamine_liberator = moderate_histamine_liberator
            food.moderate_dao_blocker = moderate_dao_blocker

            # Update high serving ratings
            food.high_fructans = high_fructans
            food.high_gos = high_gos
            food.high_lactose = high_lactose
            food.high_fructose = high_fructose
            food.high_polyols = high_polyols
            food.high_mannitol = high_mannitol
            food.high_sorbitol = high_sorbitol
            food.high_histamine_level = high_histamine_level
            food.high_histamine_liberator = high_histamine_liberator
            food.high_dao_blocker = high_dao_blocker

            # Additional information
            food.preparation_notes = request.form.get('notes', '')

            # NOTE: Nutrition fields (health_star_rating, serving_size, energy, macros, vitamins, minerals, etc.)
            # are no longer stored in the Food table. They are now read-only properties that return None.
            # Nutritional data comes from the USDA database via the usda_food relationship.
            # The form may still submit these fields, but we don't save them.

            # Custom nutrients - check for new JSON format first, fall back to old parser
            custom_nutrients_json = request.form.get('custom_nutrients', '').strip()
            if custom_nutrients_json and custom_nutrients_json != '{}':
                # New format: JSON data from custom nutrition section
                try:
                    # Validate it's proper JSON
                    json.loads(custom_nutrients_json)
                    food.custom_nutrients = custom_nutrients_json
                except json.JSONDecodeError:
                    # Invalid JSON, try old parser
                    parsed_nutrients = parse_custom_nutrients(request.form)
                    if parsed_nutrients:
                        food.custom_nutrients = parsed_nutrients
            else:
                # Try old format parser for backward compatibility
                parsed_nutrients = parse_custom_nutrients(request.form)
                if parsed_nutrients:
                    food.custom_nutrients = parsed_nutrients

            # Mark as complete since food has been edited with full information
            food.is_complete = True

            db.session.commit()

            flash(f'"{food.name}" updated successfully!', 'success')
            return redirect(url_for('compendium.detail', food_id=food.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating food: {str(e)}', 'error')
            return redirect(url_for('compendium.edit_food', food_id=food_id))

    # Parse custom nutrients JSON for template pre-population
    custom_nutrients = None
    if food.custom_nutrients:
        try:
            custom_nutrients = json.loads(food.custom_nutrients)
        except (json.JSONDecodeError, TypeError):
            custom_nutrients = None
    return render_template('compendium/edit-food.html', food=food, custom_nutrients=custom_nutrients)

@bp.route('/delete/<int:food_id>', methods=['POST'])
def delete_food(food_id):
    """Delete a food from the database"""
    food = Food.query.get_or_404(food_id)
    food_name = food.name
    food_category = food.category

    # Check for references in meals
    meal_count = MealFood.query.filter_by(food_id=food_id).count()

    # Check for references in recipes
    recipe_count = RecipeIngredient.query.filter_by(food_id=food_id).count()

    # Check for references in saved meals
    saved_meal_count = SavedMealItem.query.filter_by(food_id=food_id).count()

    total_references = meal_count + recipe_count + saved_meal_count

    if total_references > 0:
        # Build warning message
        references = []
        if meal_count > 0:
            references.append(f"{meal_count} diary meal{'s' if meal_count > 1 else ''}")
        if recipe_count > 0:
            references.append(f"{recipe_count} recipe{'s' if recipe_count > 1 else ''}")
        if saved_meal_count > 0:
            references.append(f"{saved_meal_count} saved meal{'s' if saved_meal_count > 1 else ''}")

        warning = f"Cannot delete '{food_name}'. It is used in: {', '.join(references)}."
        flash(warning, 'danger')
        return redirect(url_for('compendium.detail', food_id=food_id))

    # Safe to delete
    try:
        db.session.delete(food)
        db.session.commit()
        flash(f'"{food_name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting food: {str(e)}', 'error')

    # Redirect back to the category search or general search
    return redirect(url_for('compendium.search', category=food_category))

