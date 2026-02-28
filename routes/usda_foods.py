"""
USDA Foods Routes
=================
Routes for browsing USDA FoodData Central database.
"""

from flask import Blueprint, render_template, request

from database import db
from models.usda import USDAFoodCategory, USDAFood, USDANutrient, USDAFoodNutrient, USDAFoodPortion

bp = Blueprint('usda_foods', __name__, url_prefix='/usda-foods')


@bp.route('/categories')
def categories():
    """Browse categories, optionally filtered by data type"""
    from sqlalchemy import func

    data_type = request.args.get('type', '')

    # Get categories with food counts for the selected data type
    if data_type:
        # Count foods per category for this data type
        category_counts = db.session.query(
            USDAFoodCategory.id,
            USDAFoodCategory.description,
            func.count(USDAFood.id).label('count')
        ).join(USDAFood, USDAFood.category_id == USDAFoodCategory.id
        ).filter(USDAFood.data_type == data_type
        ).group_by(USDAFoodCategory.id, USDAFoodCategory.description
        ).having(func.count(USDAFood.id) > 0
        ).order_by(USDAFoodCategory.description).all()

        categories_list = [
            {'id': c.id, 'description': c.description, 'food_count': c.count}
            for c in category_counts
        ]
        total_foods = sum(c['food_count'] for c in categories_list)
    else:
        # Show all categories with their total counts
        all_categories = USDAFoodCategory.query.filter(
            USDAFoodCategory.food_count > 0
        ).order_by(USDAFoodCategory.description).all()
        categories_list = [
            {'id': c.id, 'description': c.description, 'food_count': c.food_count}
            for c in all_categories
        ]
        total_foods = USDAFood.query.count()

    # Get counts for sidebar stats
    foundation_count = USDAFood.query.filter_by(data_type='Foundation').count()
    sr_legacy_count = USDAFood.query.filter_by(data_type='SR Legacy').count()
    survey_count = USDAFood.query.filter_by(data_type='Survey').count()
    branded_count = USDAFood.query.filter_by(data_type='Branded').count()

    # Get count for the selected data type (for empty categories message)
    data_type_food_count = 0
    if data_type:
        data_type_food_count = USDAFood.query.filter_by(data_type=data_type).count()

    return render_template(
        'usda_foods/categories.html',
        categories=categories_list,
        data_type=data_type,
        total_foods=total_foods,
        foundation_count=foundation_count,
        sr_legacy_count=sr_legacy_count,
        survey_count=survey_count,
        branded_count=branded_count,
        category_count=len(categories_list),
        data_type_food_count=data_type_food_count
    )


@bp.route('/search')
def search():
    """Search and browse USDA foods"""
    query = request.args.get('q', '').strip()
    category_id = request.args.get('category', type=int)
    data_type = request.args.get('type', '')
    letter = request.args.get('letter', '').upper()

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
        foods_query = foods_query.filter_by(data_type=data_type)

    # Filter by starting letter
    if letter and len(letter) == 1 and letter.isalpha():
        foods_query = foods_query.filter(USDAFood.description.ilike(f'{letter}%'))

    # Order by name
    foods_query = foods_query.order_by(USDAFood.description)

    # Get available letters for this category (for alphabet nav)
    available_letters = []
    if category_id:
        # Get distinct first letters for foods in this category
        from sqlalchemy import func
        letter_query = db.session.query(
            func.upper(func.substr(USDAFood.description, 1, 1)).label('letter')
        ).filter(USDAFood.category_id == category_id)
        if data_type:
            letter_query = letter_query.filter(USDAFood.data_type == data_type)
        letter_query = letter_query.distinct().order_by('letter')
        available_letters = [r.letter for r in letter_query.all() if r.letter and r.letter.isalpha()]

    # Limit results for performance (unless filtering by letter or specific category)
    if not category_id and not query and not letter:
        foods = foods_query.limit(100).all()
        showing_limited = True
    elif letter:
        # Show all foods for selected letter
        foods = foods_query.all()
        showing_limited = False
    else:
        foods = foods_query.limit(500).all()
        showing_limited = len(foods) >= 500

    # Get all categories for sidebar filter
    categories = USDAFoodCategory.query.filter(
        USDAFoodCategory.food_count > 0
    ).order_by(USDAFoodCategory.description).all()

    # Get current category name if filtering
    current_category = None
    if category_id:
        current_category = USDAFoodCategory.query.get(category_id)

    return render_template(
        'usda_foods/search.html',
        foods=foods,
        query=query,
        categories=categories,
        current_category=current_category,
        data_type=data_type,
        letter=letter,
        available_letters=available_letters,
        showing_limited=showing_limited,
        food_count=len(foods)
    )


@bp.route('/<int:food_id>')
def detail(food_id):
    """View details of a single USDA food"""
    food = USDAFood.query.get_or_404(food_id)

    # Get nutrients organized by group
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

    # Define display order for groups
    group_order = ['Energy', 'Proximates', 'Minerals', 'Vitamins', 'Lipids', 'Amino Acids', 'Other']

    # Get portions
    portions = food.portions.order_by(USDAFoodPortion.sequence_number).all()

    return render_template(
        'usda_foods/detail.html',
        food=food,
        nutrients_by_group=nutrients_by_group,
        group_order=group_order,
        portions=portions
    )
