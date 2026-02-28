"""
AUSNUT 2023 Foods Routes
=========================
Routes for browsing the AUSNUT 2023 Australian food database.
"""

from flask import Blueprint, render_template, request
from sqlalchemy import func

from database import db
from models.ausnut import AUSNUTFood, AUSNUTNutrient, AUSNUTFoodNutrient

bp = Blueprint('ausnut_foods', __name__, url_prefix='/ausnut-foods')


@bp.route('/search')
def search():
    """Search and browse AUSNUT foods"""
    query = request.args.get('q', '').strip()
    letter = request.args.get('letter', '').upper()

    foods_query = AUSNUTFood.query

    if query:
        foods_query = foods_query.filter(AUSNUTFood.food_name.ilike(f'%{query}%'))

    if letter and len(letter) == 1 and letter.isalpha():
        foods_query = foods_query.filter(AUSNUTFood.food_name.ilike(f'{letter}%'))

    foods_query = foods_query.order_by(AUSNUTFood.food_name)

    # Get available letters for alphabet nav
    letter_query = db.session.query(
        func.upper(func.substr(AUSNUTFood.food_name, 1, 1)).label('letter')
    )
    if query:
        letter_query = letter_query.filter(AUSNUTFood.food_name.ilike(f'%{query}%'))
    letter_query = letter_query.distinct().order_by('letter')
    available_letters = [r.letter for r in letter_query.all() if r.letter and r.letter.isalpha()]

    # Limit results
    if not query and not letter:
        foods = foods_query.limit(100).all()
        showing_limited = True
    elif letter:
        foods = foods_query.all()
        showing_limited = False
    else:
        foods = foods_query.limit(500).all()
        showing_limited = len(foods) >= 500

    return render_template(
        'ausnut_foods/search.html',
        foods=foods,
        query=query,
        letter=letter,
        available_letters=available_letters,
        showing_limited=showing_limited,
        food_count=len(foods)
    )


@bp.route('/<int:food_id>')
def detail(food_id):
    """View details of a single AUSNUT food"""
    food = AUSNUTFood.query.get_or_404(food_id)

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

    for group in nutrients_by_group:
        nutrients_by_group[group].sort(key=lambda x: (x['rank'], x['name']))

    group_order = ['Energy', 'Macronutrients', 'Vitamins', 'Minerals', 'Fats', 'Other']

    return render_template(
        'ausnut_foods/detail.html',
        food=food,
        nutrients_by_group=nutrients_by_group,
        group_order=group_order
    )
