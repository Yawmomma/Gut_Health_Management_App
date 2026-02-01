from flask import Blueprint, render_template, jsonify
from datetime import datetime, timedelta, date
from models.diary import DiaryEntry, Meal, MealFood
from models.food import Food
from database import db

bp = Blueprint('main', __name__)


def get_traffic_light_color(food, serving_type):
    """
    Determine the traffic light color for a food at a given serving type.
    Returns 'green', 'amber', or 'red' based on worst FODMAP/histamine rating.
    """
    # Normalize serving_type to handle variations
    if serving_type:
        serving_type = serving_type.lower().strip()

    if serving_type in ['moderate', 'medium']:
        fodmap_ratings = [
            food.moderate_fructans, food.moderate_gos, food.moderate_lactose,
            food.moderate_fructose, food.moderate_polyols, food.moderate_mannitol,
            food.moderate_sorbitol
        ]
        histamine_level = food.moderate_histamine_level
        dao_blocker = food.moderate_dao_blocker
        liberator = food.moderate_histamine_liberator
    elif serving_type == 'high':
        fodmap_ratings = [
            food.high_fructans, food.high_gos, food.high_lactose,
            food.high_fructose, food.high_polyols, food.high_mannitol,
            food.high_sorbitol
        ]
        histamine_level = food.high_histamine_level
        dao_blocker = food.high_dao_blocker
        liberator = food.high_histamine_liberator
    elif serving_type in ['safe', 'low', None, '']:
        # Safe serving - check safe serving ratings
        fodmap_ratings = [
            food.safe_fructans, food.safe_gos, food.safe_lactose,
            food.safe_fructose, food.safe_polyols, food.safe_mannitol,
            food.safe_sorbitol
        ]
        histamine_level = food.safe_histamine_level
        dao_blocker = food.safe_dao_blocker
        liberator = food.safe_histamine_liberator
    else:
        # Unknown serving type - default to safe (green)
        return 'green'

    # Check FODMAP ratings
    for rating in fodmap_ratings:
        if rating and rating.lower() in ['red', 'high']:
            return 'red'

    # Check histamine
    if histamine_level and histamine_level.lower() in ['high']:
        return 'red'
    if dao_blocker and dao_blocker.lower() == 'yes':
        return 'red'
    if liberator and liberator.lower() == 'yes':
        return 'red'

    # Check for amber/moderate
    for rating in fodmap_ratings:
        if rating and rating.lower() in ['amber', 'medium', 'moderate']:
            return 'amber'

    if histamine_level and histamine_level.lower() in ['medium', 'moderate']:
        return 'amber'

    return 'green'


@bp.route('/dashboard')
def dashboard():
    """Main dashboard view"""
    # Get foods logged in the last 7 days that have moderate or high serving concerns
    today = date.today()
    week_ago = today - timedelta(days=7)

    # Query meal foods from the last 7 days
    recent_meal_foods = db.session.query(MealFood, DiaryEntry).join(
        Meal, MealFood.meal_id == Meal.id
    ).join(
        DiaryEntry, Meal.diary_entry_id == DiaryEntry.id
    ).filter(
        DiaryEntry.entry_date >= week_ago,
        DiaryEntry.entry_type == 'meal'
    ).order_by(DiaryEntry.entry_date.desc()).all()

    # Build watch list - foods with concerning FODMAP/histamine levels
    # Check each food's ratings at moderate and high serving sizes
    watch_list = []
    seen_food_ids = set()

    for meal_food, diary_entry in recent_meal_foods:
        food = meal_food.food
        if not food or food.id in seen_food_ids:
            continue

        # Get the serving type that was actually logged in the diary
        logged_serving_type = meal_food.serving_type  # 'safe', 'moderate', or 'high'

        # Get the traffic light color for the ACTUAL serving size that was consumed
        actual_color = get_traffic_light_color(food, logged_serving_type)

        # Determine risk level based on the actual serving consumed
        # High risk = red rating at the logged serving size
        # Moderate risk = amber rating at the logged serving size
        level = None
        if actual_color == 'red':
            level = 'high'
        elif actual_color == 'amber':
            level = 'moderate'
        # 'green' = no concern, don't add to watch list

        # Only add if there's a concerning level
        if level:
            watch_list.append({
                'food': food,
                'level': level,
                'logged_date': diary_entry.entry_date,
                'diary_date_string': diary_entry.entry_date.strftime('%Y-%m-%d'),
                'portion_size': meal_food.portion_size,
                'serving_type': logged_serving_type
            })
            seen_food_ids.add(food.id)

    # Separate and sort watch list by risk level
    high_risk_foods = sorted(
        [x for x in watch_list if x['level'] == 'high'],
        key=lambda x: x['logged_date'],
        reverse=True
    )
    moderate_risk_foods = sorted(
        [x for x in watch_list if x['level'] == 'moderate'],
        key=lambda x: x['logged_date'],
        reverse=True
    )

    # Query for incomplete foods (quick-added foods that need more information)
    incomplete_foods = Food.query.filter_by(is_complete=False).order_by(Food.created_at.desc()).all()

    return render_template('dashboard/index.html',
                         current_date=datetime.now(),
                         high_risk_foods=high_risk_foods,
                         moderate_risk_foods=moderate_risk_foods,
                         incomplete_foods=incomplete_foods)

@bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')
