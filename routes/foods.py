from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from models.food import Food
from models.diary import MealFood
from models.recipe import RecipeIngredient, SavedMealItem
from database import db
import json

bp = Blueprint('foods', __name__, url_prefix='/foods')


def parse_custom_nutrients(form):
    """Parse custom nutrients from form data and return as JSON string"""
    def safe_float(value):
        """Safely convert to float, returning None for empty/invalid values"""
        if value is None or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

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
            'per_serve': safe_float(form.get(f'custom_vitamin_per_serve_{i}')),
            'per_100': safe_float(form.get(f'custom_vitamin_per_100_{i}')),
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
            'per_serve': safe_float(form.get(f'custom_mineral_per_serve_{i}')),
            'per_100': safe_float(form.get(f'custom_mineral_per_100_{i}')),
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
            'per_serve': safe_float(form.get(f'custom_macro_per_serve_{i}')),
            'per_100': safe_float(form.get(f'custom_macro_per_100_{i}')),
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
    """Food guide home page"""
    return render_template('foods/index.html')

@bp.route('/search')
def search():
    """Food search interface"""
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    view_all = request.args.get('view_all', '')

    foods = Food.query

    if query:
        foods = foods.filter(Food.name.ilike(f'%{query}%'))

    if category:
        foods = foods.filter_by(category=category)

    foods = foods.order_by(Food.name).all()

    return render_template('foods/search.html',
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
    recipe_count = RecipeIngredient.query.filter_by(food_id=food_id).count()
    saved_meal_count = SavedMealItem.query.filter_by(food_id=food_id).count()

    # Parse custom nutrients JSON for template
    custom_nutrients = None
    if food.custom_nutrients:
        try:
            custom_nutrients = json.loads(food.custom_nutrients)
        except (json.JSONDecodeError, TypeError):
            custom_nutrients = None

    return render_template('foods/detail.html',
                         food=food,
                         custom_nutrients=custom_nutrients,
                         meal_count=meal_count,
                         recipe_count=recipe_count,
                         saved_meal_count=saved_meal_count)

@bp.route('/compare')
def compare():
    """Compare multiple foods"""
    food_ids = request.args.getlist('ids')
    foods = Food.query.filter(Food.id.in_(food_ids)).order_by(Food.name).all() if food_ids else []
    return render_template('foods/compare.html', foods=foods)

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

            # Nutrition information (optional)
            health_star_rating = request.form.get('health_star_rating')
            serving_size = request.form.get('serving_size', '')
            servings_per_pack = request.form.get('servings_per_pack')

            # Energy
            energy_per_serve_kj = request.form.get('energy_per_serve_kj')
            energy_per_100_kj = request.form.get('energy_per_100_kj')
            energy_per_serve_cal = request.form.get('energy_per_serve_cal')
            energy_per_100_cal = request.form.get('energy_per_100_cal')

            # Macronutrients per serve
            protein_per_serve = request.form.get('protein_per_serve')
            fat_per_serve = request.form.get('fat_per_serve')
            saturated_fat_per_serve = request.form.get('saturated_fat_per_serve')
            trans_fat_per_serve = request.form.get('trans_fat_per_serve')
            polyunsaturated_fat_per_serve = request.form.get('polyunsaturated_fat_per_serve')
            monounsaturated_fat_per_serve = request.form.get('monounsaturated_fat_per_serve')
            carbohydrate_per_serve = request.form.get('carbohydrate_per_serve')
            sugars_per_serve = request.form.get('sugars_per_serve')
            lactose_per_serve = request.form.get('lactose_per_serve')
            galactose_per_serve = request.form.get('galactose_per_serve')
            dietary_fibre_per_serve = request.form.get('dietary_fibre_per_serve')

            # Macronutrients per 100
            protein_per_100 = request.form.get('protein_per_100')
            fat_per_100 = request.form.get('fat_per_100')
            saturated_fat_per_100 = request.form.get('saturated_fat_per_100')
            trans_fat_per_100 = request.form.get('trans_fat_per_100')
            polyunsaturated_fat_per_100 = request.form.get('polyunsaturated_fat_per_100')
            monounsaturated_fat_per_100 = request.form.get('monounsaturated_fat_per_100')
            carbohydrate_per_100 = request.form.get('carbohydrate_per_100')
            sugars_per_100 = request.form.get('sugars_per_100')
            lactose_per_100 = request.form.get('lactose_per_100')
            galactose_per_100 = request.form.get('galactose_per_100')
            dietary_fibre_per_100 = request.form.get('dietary_fibre_per_100')

            # Cholesterol
            cholesterol_per_serve = request.form.get('cholesterol_per_serve')
            cholesterol_per_100 = request.form.get('cholesterol_per_100')

            # Minerals per serve
            sodium_per_serve = request.form.get('sodium_per_serve')
            potassium_per_serve = request.form.get('potassium_per_serve')
            calcium_per_serve = request.form.get('calcium_per_serve')
            phosphorus_per_serve = request.form.get('phosphorus_per_serve')

            # Minerals per 100
            sodium_per_100 = request.form.get('sodium_per_100')
            potassium_per_100 = request.form.get('potassium_per_100')
            calcium_per_100 = request.form.get('calcium_per_100')
            phosphorus_per_100 = request.form.get('phosphorus_per_100')

            # Vitamins per serve
            vitamin_a_per_serve = request.form.get('vitamin_a_per_serve')
            vitamin_b12_per_serve = request.form.get('vitamin_b12_per_serve')
            vitamin_d_per_serve = request.form.get('vitamin_d_per_serve')
            riboflavin_b2_per_serve = request.form.get('riboflavin_b2_per_serve')

            # Vitamins per 100
            vitamin_a_per_100 = request.form.get('vitamin_a_per_100')
            vitamin_b12_per_100 = request.form.get('vitamin_b12_per_100')
            vitamin_d_per_100 = request.form.get('vitamin_d_per_100')
            riboflavin_b2_per_100 = request.form.get('riboflavin_b2_per_100')

            # RDI percentages
            vitamin_a_rdi_percent = request.form.get('vitamin_a_rdi_percent', '')
            vitamin_b12_rdi_percent = request.form.get('vitamin_b12_rdi_percent', '')
            vitamin_d_rdi_percent = request.form.get('vitamin_d_rdi_percent', '')
            riboflavin_b2_rdi_percent = request.form.get('riboflavin_b2_rdi_percent', '')
            calcium_rdi_percent = request.form.get('calcium_rdi_percent', '')
            phosphorus_rdi_percent = request.form.get('phosphorus_rdi_percent', '')

            # Ingredients and where to buy
            ingredients_list = request.form.get('ingredients_list', '')
            contains_allergens = request.form.get('contains_allergens', '')
            may_contain_allergens = request.form.get('may_contain_allergens', '')
            where_to_buy = request.form.get('where_to_buy', '')

            # Create new food
            # Foods created via full form are marked as complete
            new_food = Food(
                name=food_name,
                category=category,
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
                # Nutrition information
                health_star_rating=float(health_star_rating) if health_star_rating else None,
                serving_size=serving_size,
                servings_per_pack=int(servings_per_pack) if servings_per_pack else None,
                # Energy
                energy_per_serve_kj=float(energy_per_serve_kj) if energy_per_serve_kj else None,
                energy_per_100_kj=float(energy_per_100_kj) if energy_per_100_kj else None,
                energy_per_serve_cal=float(energy_per_serve_cal) if energy_per_serve_cal else None,
                energy_per_100_cal=float(energy_per_100_cal) if energy_per_100_cal else None,
                # Macronutrients per serve
                protein_per_serve=float(protein_per_serve) if protein_per_serve else None,
                fat_per_serve=float(fat_per_serve) if fat_per_serve else None,
                saturated_fat_per_serve=float(saturated_fat_per_serve) if saturated_fat_per_serve else None,
                trans_fat_per_serve=float(trans_fat_per_serve) if trans_fat_per_serve else None,
                polyunsaturated_fat_per_serve=float(polyunsaturated_fat_per_serve) if polyunsaturated_fat_per_serve else None,
                monounsaturated_fat_per_serve=float(monounsaturated_fat_per_serve) if monounsaturated_fat_per_serve else None,
                carbohydrate_per_serve=float(carbohydrate_per_serve) if carbohydrate_per_serve else None,
                sugars_per_serve=float(sugars_per_serve) if sugars_per_serve else None,
                lactose_per_serve=float(lactose_per_serve) if lactose_per_serve else None,
                galactose_per_serve=float(galactose_per_serve) if galactose_per_serve else None,
                dietary_fibre_per_serve=float(dietary_fibre_per_serve) if dietary_fibre_per_serve else None,
                # Macronutrients per 100
                protein_per_100=float(protein_per_100) if protein_per_100 else None,
                fat_per_100=float(fat_per_100) if fat_per_100 else None,
                saturated_fat_per_100=float(saturated_fat_per_100) if saturated_fat_per_100 else None,
                trans_fat_per_100=float(trans_fat_per_100) if trans_fat_per_100 else None,
                polyunsaturated_fat_per_100=float(polyunsaturated_fat_per_100) if polyunsaturated_fat_per_100 else None,
                monounsaturated_fat_per_100=float(monounsaturated_fat_per_100) if monounsaturated_fat_per_100 else None,
                carbohydrate_per_100=float(carbohydrate_per_100) if carbohydrate_per_100 else None,
                sugars_per_100=float(sugars_per_100) if sugars_per_100 else None,
                lactose_per_100=float(lactose_per_100) if lactose_per_100 else None,
                galactose_per_100=float(galactose_per_100) if galactose_per_100 else None,
                dietary_fibre_per_100=float(dietary_fibre_per_100) if dietary_fibre_per_100 else None,
                # Cholesterol
                cholesterol_per_serve=float(cholesterol_per_serve) if cholesterol_per_serve else None,
                cholesterol_per_100=float(cholesterol_per_100) if cholesterol_per_100 else None,
                # Minerals per serve
                sodium_per_serve=float(sodium_per_serve) if sodium_per_serve else None,
                potassium_per_serve=float(potassium_per_serve) if potassium_per_serve else None,
                calcium_per_serve=float(calcium_per_serve) if calcium_per_serve else None,
                phosphorus_per_serve=float(phosphorus_per_serve) if phosphorus_per_serve else None,
                # Minerals per 100
                sodium_per_100=float(sodium_per_100) if sodium_per_100 else None,
                potassium_per_100=float(potassium_per_100) if potassium_per_100 else None,
                calcium_per_100=float(calcium_per_100) if calcium_per_100 else None,
                phosphorus_per_100=float(phosphorus_per_100) if phosphorus_per_100 else None,
                # Vitamins per serve
                vitamin_a_per_serve=float(vitamin_a_per_serve) if vitamin_a_per_serve else None,
                vitamin_b12_per_serve=float(vitamin_b12_per_serve) if vitamin_b12_per_serve else None,
                vitamin_d_per_serve=float(vitamin_d_per_serve) if vitamin_d_per_serve else None,
                riboflavin_b2_per_serve=float(riboflavin_b2_per_serve) if riboflavin_b2_per_serve else None,
                # Vitamins per 100
                vitamin_a_per_100=float(vitamin_a_per_100) if vitamin_a_per_100 else None,
                vitamin_b12_per_100=float(vitamin_b12_per_100) if vitamin_b12_per_100 else None,
                vitamin_d_per_100=float(vitamin_d_per_100) if vitamin_d_per_100 else None,
                riboflavin_b2_per_100=float(riboflavin_b2_per_100) if riboflavin_b2_per_100 else None,
                # RDI percentages
                vitamin_a_rdi_percent=vitamin_a_rdi_percent,
                vitamin_b12_rdi_percent=vitamin_b12_rdi_percent,
                vitamin_d_rdi_percent=vitamin_d_rdi_percent,
                riboflavin_b2_rdi_percent=riboflavin_b2_rdi_percent,
                calcium_rdi_percent=calcium_rdi_percent,
                phosphorus_rdi_percent=phosphorus_rdi_percent,
                # Ingredients and where to buy
                ingredients_list=ingredients_list,
                contains_allergens=contains_allergens,
                may_contain_allergens=may_contain_allergens,
                where_to_buy=where_to_buy,
                # Custom nutrients
                custom_nutrients=parse_custom_nutrients(request.form),
                # Mark as complete since it was created via full form
                is_complete=True
            )

            db.session.add(new_food)
            db.session.commit()

            flash(f'"{food_name}" added successfully!', 'success')
            return redirect(url_for('foods.detail', food_id=new_food.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error adding food: {str(e)}', 'error')
            return redirect(url_for('foods.add_food'))

    return render_template('foods/add-food.html')

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

            # Nutrition information (optional)
            health_star_rating = request.form.get('health_star_rating')
            food.health_star_rating = float(health_star_rating) if health_star_rating else None
            food.serving_size = request.form.get('serving_size', '')
            servings_per_pack = request.form.get('servings_per_pack')
            food.servings_per_pack = int(servings_per_pack) if servings_per_pack else None

            # Energy
            energy_per_serve_kj = request.form.get('energy_per_serve_kj')
            food.energy_per_serve_kj = float(energy_per_serve_kj) if energy_per_serve_kj else None
            energy_per_100_kj = request.form.get('energy_per_100_kj')
            food.energy_per_100_kj = float(energy_per_100_kj) if energy_per_100_kj else None
            energy_per_serve_cal = request.form.get('energy_per_serve_cal')
            food.energy_per_serve_cal = float(energy_per_serve_cal) if energy_per_serve_cal else None
            energy_per_100_cal = request.form.get('energy_per_100_cal')
            food.energy_per_100_cal = float(energy_per_100_cal) if energy_per_100_cal else None

            # Macronutrients per serve
            protein_per_serve = request.form.get('protein_per_serve')
            food.protein_per_serve = float(protein_per_serve) if protein_per_serve else None
            fat_per_serve = request.form.get('fat_per_serve')
            food.fat_per_serve = float(fat_per_serve) if fat_per_serve else None
            saturated_fat_per_serve = request.form.get('saturated_fat_per_serve')
            food.saturated_fat_per_serve = float(saturated_fat_per_serve) if saturated_fat_per_serve else None
            trans_fat_per_serve = request.form.get('trans_fat_per_serve')
            food.trans_fat_per_serve = float(trans_fat_per_serve) if trans_fat_per_serve else None
            polyunsaturated_fat_per_serve = request.form.get('polyunsaturated_fat_per_serve')
            food.polyunsaturated_fat_per_serve = float(polyunsaturated_fat_per_serve) if polyunsaturated_fat_per_serve else None
            monounsaturated_fat_per_serve = request.form.get('monounsaturated_fat_per_serve')
            food.monounsaturated_fat_per_serve = float(monounsaturated_fat_per_serve) if monounsaturated_fat_per_serve else None
            carbohydrate_per_serve = request.form.get('carbohydrate_per_serve')
            food.carbohydrate_per_serve = float(carbohydrate_per_serve) if carbohydrate_per_serve else None
            sugars_per_serve = request.form.get('sugars_per_serve')
            food.sugars_per_serve = float(sugars_per_serve) if sugars_per_serve else None
            lactose_per_serve = request.form.get('lactose_per_serve')
            food.lactose_per_serve = float(lactose_per_serve) if lactose_per_serve else None
            galactose_per_serve = request.form.get('galactose_per_serve')
            food.galactose_per_serve = float(galactose_per_serve) if galactose_per_serve else None
            dietary_fibre_per_serve = request.form.get('dietary_fibre_per_serve')
            food.dietary_fibre_per_serve = float(dietary_fibre_per_serve) if dietary_fibre_per_serve else None

            # Macronutrients per 100
            protein_per_100 = request.form.get('protein_per_100')
            food.protein_per_100 = float(protein_per_100) if protein_per_100 else None
            fat_per_100 = request.form.get('fat_per_100')
            food.fat_per_100 = float(fat_per_100) if fat_per_100 else None
            saturated_fat_per_100 = request.form.get('saturated_fat_per_100')
            food.saturated_fat_per_100 = float(saturated_fat_per_100) if saturated_fat_per_100 else None
            trans_fat_per_100 = request.form.get('trans_fat_per_100')
            food.trans_fat_per_100 = float(trans_fat_per_100) if trans_fat_per_100 else None
            polyunsaturated_fat_per_100 = request.form.get('polyunsaturated_fat_per_100')
            food.polyunsaturated_fat_per_100 = float(polyunsaturated_fat_per_100) if polyunsaturated_fat_per_100 else None
            monounsaturated_fat_per_100 = request.form.get('monounsaturated_fat_per_100')
            food.monounsaturated_fat_per_100 = float(monounsaturated_fat_per_100) if monounsaturated_fat_per_100 else None
            carbohydrate_per_100 = request.form.get('carbohydrate_per_100')
            food.carbohydrate_per_100 = float(carbohydrate_per_100) if carbohydrate_per_100 else None
            sugars_per_100 = request.form.get('sugars_per_100')
            food.sugars_per_100 = float(sugars_per_100) if sugars_per_100 else None
            lactose_per_100 = request.form.get('lactose_per_100')
            food.lactose_per_100 = float(lactose_per_100) if lactose_per_100 else None
            galactose_per_100 = request.form.get('galactose_per_100')
            food.galactose_per_100 = float(galactose_per_100) if galactose_per_100 else None
            dietary_fibre_per_100 = request.form.get('dietary_fibre_per_100')
            food.dietary_fibre_per_100 = float(dietary_fibre_per_100) if dietary_fibre_per_100 else None

            # Cholesterol
            cholesterol_per_serve = request.form.get('cholesterol_per_serve')
            food.cholesterol_per_serve = float(cholesterol_per_serve) if cholesterol_per_serve else None
            cholesterol_per_100 = request.form.get('cholesterol_per_100')
            food.cholesterol_per_100 = float(cholesterol_per_100) if cholesterol_per_100 else None

            # Minerals per serve
            sodium_per_serve = request.form.get('sodium_per_serve')
            food.sodium_per_serve = float(sodium_per_serve) if sodium_per_serve else None
            potassium_per_serve = request.form.get('potassium_per_serve')
            food.potassium_per_serve = float(potassium_per_serve) if potassium_per_serve else None
            calcium_per_serve = request.form.get('calcium_per_serve')
            food.calcium_per_serve = float(calcium_per_serve) if calcium_per_serve else None
            phosphorus_per_serve = request.form.get('phosphorus_per_serve')
            food.phosphorus_per_serve = float(phosphorus_per_serve) if phosphorus_per_serve else None

            # Minerals per 100
            sodium_per_100 = request.form.get('sodium_per_100')
            food.sodium_per_100 = float(sodium_per_100) if sodium_per_100 else None
            potassium_per_100 = request.form.get('potassium_per_100')
            food.potassium_per_100 = float(potassium_per_100) if potassium_per_100 else None
            calcium_per_100 = request.form.get('calcium_per_100')
            food.calcium_per_100 = float(calcium_per_100) if calcium_per_100 else None
            phosphorus_per_100 = request.form.get('phosphorus_per_100')
            food.phosphorus_per_100 = float(phosphorus_per_100) if phosphorus_per_100 else None

            # Vitamins per serve
            vitamin_a_per_serve = request.form.get('vitamin_a_per_serve')
            food.vitamin_a_per_serve = float(vitamin_a_per_serve) if vitamin_a_per_serve else None
            vitamin_b12_per_serve = request.form.get('vitamin_b12_per_serve')
            food.vitamin_b12_per_serve = float(vitamin_b12_per_serve) if vitamin_b12_per_serve else None
            vitamin_d_per_serve = request.form.get('vitamin_d_per_serve')
            food.vitamin_d_per_serve = float(vitamin_d_per_serve) if vitamin_d_per_serve else None
            riboflavin_b2_per_serve = request.form.get('riboflavin_b2_per_serve')
            food.riboflavin_b2_per_serve = float(riboflavin_b2_per_serve) if riboflavin_b2_per_serve else None

            # Vitamins per 100
            vitamin_a_per_100 = request.form.get('vitamin_a_per_100')
            food.vitamin_a_per_100 = float(vitamin_a_per_100) if vitamin_a_per_100 else None
            vitamin_b12_per_100 = request.form.get('vitamin_b12_per_100')
            food.vitamin_b12_per_100 = float(vitamin_b12_per_100) if vitamin_b12_per_100 else None
            vitamin_d_per_100 = request.form.get('vitamin_d_per_100')
            food.vitamin_d_per_100 = float(vitamin_d_per_100) if vitamin_d_per_100 else None
            riboflavin_b2_per_100 = request.form.get('riboflavin_b2_per_100')
            food.riboflavin_b2_per_100 = float(riboflavin_b2_per_100) if riboflavin_b2_per_100 else None

            # RDI percentages
            food.vitamin_a_rdi_percent = request.form.get('vitamin_a_rdi_percent', '')
            food.vitamin_b12_rdi_percent = request.form.get('vitamin_b12_rdi_percent', '')
            food.vitamin_d_rdi_percent = request.form.get('vitamin_d_rdi_percent', '')
            food.riboflavin_b2_rdi_percent = request.form.get('riboflavin_b2_rdi_percent', '')
            food.calcium_rdi_percent = request.form.get('calcium_rdi_percent', '')
            food.phosphorus_rdi_percent = request.form.get('phosphorus_rdi_percent', '')

            # Ingredients and where to buy
            food.ingredients_list = request.form.get('ingredients_list', '')
            food.contains_allergens = request.form.get('contains_allergens', '')
            food.may_contain_allergens = request.form.get('may_contain_allergens', '')
            food.where_to_buy = request.form.get('where_to_buy', '')

            # Custom nutrients
            food.custom_nutrients = parse_custom_nutrients(request.form)

            # Mark as complete since food has been edited with full information
            food.is_complete = True

            db.session.commit()

            flash(f'"{food.name}" updated successfully!', 'success')
            return redirect(url_for('foods.detail', food_id=food.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating food: {str(e)}', 'error')
            return redirect(url_for('foods.edit_food', food_id=food_id))

    # Parse custom nutrients JSON for template pre-population
    custom_nutrients = None
    if food.custom_nutrients:
        try:
            custom_nutrients = json.loads(food.custom_nutrients)
        except (json.JSONDecodeError, TypeError):
            custom_nutrients = None
    return render_template('foods/edit-food.html', food=food, custom_nutrients=custom_nutrients)

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
        return redirect(url_for('foods.detail', food_id=food_id))

    # Safe to delete
    try:
        db.session.delete(food)
        db.session.commit()
        flash(f'"{food_name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting food: {str(e)}', 'error')

    # Redirect back to the category search or general search
    return redirect(url_for('foods.search', category=food_category))

@bp.route('/safe-foods')
def safe_foods():
    """List of safe foods (low FODMAP and low histamine)"""
    # Query foods that are safe (all green FODMAPs and low histamine)
    foods = Food.query.filter(
        Food.fructans == 'Green',
        Food.gos == 'Green',
        Food.lactose == 'Green',
        Food.fructose == 'Green',
        Food.polyols == 'Green',
        Food.histamine_level == 'Low',
        Food.dao_blocker == 'No',
        Food.histamine_liberator == 'No'
    ).order_by(Food.category, Food.name).all()

    # Group foods by category
    foods_by_category = {}
    for food in foods:
        category = food.category or 'Other'
        if category not in foods_by_category:
            foods_by_category[category] = []
        foods_by_category[category].append(food)

    return render_template('foods/safe-foods.html', foods_by_category=foods_by_category, total_count=len(foods))
