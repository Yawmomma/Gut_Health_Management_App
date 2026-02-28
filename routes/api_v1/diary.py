"""
Diary API v1 Endpoints
Provides API access to diary entry data (meals, symptoms, bowel movements, stress, notes)
"""

from flask import request, jsonify
from datetime import date, datetime, timedelta
from collections import defaultdict
from database import db
from models.diary import DiaryEntry, Meal, Symptom, BowelMovement, StressLog, Note, MealFood
from models.food import Food
from models.recipe import Recipe, SavedMeal
from . import bp
from utils.validators import (
    validate_year_month, validate_date_string, validate_optional_int,
    validate_array_size, ValidationError
)
from utils.auth import require_api_key, require_scope
from sqlalchemy.orm import joinedload

# Import nutrition calculation helpers from shared utils
from utils.nutrition import parse_portion_and_calculate_nutrition, calculate_nutrition_breakdown


def serialize_diary_entry(entry):
    """Convert a diary entry to API-friendly dictionary"""
    data = {
        'id': entry.id,
        'date': entry.entry_date.isoformat() if entry.entry_date else None,
        'time': entry.entry_time.strftime('%H:%M') if entry.entry_time else None,
        'type': entry.entry_type,
        'created_at': entry.created_at.isoformat() if entry.created_at else None
    }

    # Add type-specific details
    if entry.entry_type == 'meal':
        data['meals'] = []
        for meal in entry.meals:
            meal_data = {
                'id': meal.id,
                'meal_type': meal.meal_type,
                'location': meal.location,
                'preparation': meal.preparation,
                'recipe_id': meal.recipe_id,
                'notes': meal.notes,
                'foods': []
            }
            for mf in meal.meal_foods:
                if mf.food:
                    meal_data['foods'].append({
                        'food_id': mf.food.id,
                        'food_name': mf.food.name,
                        'portion_size': mf.portion_size,
                        'serving_type': mf.serving_type,
                        'num_servings': mf.num_servings,
                        'energy_kj': mf.energy_kj,
                        'protein_g': mf.protein_g,
                        'fat_g': mf.fat_g,
                        'carbs_g': mf.carbs_g,
                        'sodium_mg': mf.sodium_mg
                    })
            data['meals'].append(meal_data)

    elif entry.entry_type == 'symptom':
        if entry.symptoms:
            symptom = entry.symptoms[0]
            data['symptom'] = {
                'bloating': symptom.bloating,
                'pain': symptom.pain,
                'wind': symptom.wind,
                'nausea': symptom.nausea,
                'heartburn': symptom.heartburn,
                'headache': symptom.headache,
                'brain_fog': symptom.brain_fog,
                'fatigue': symptom.fatigue,
                'sinus_issues': symptom.sinus_issues,
                'severity': symptom.severity,
                'duration': symptom.duration,
                'notes': symptom.notes
            }

    elif entry.entry_type == 'bowel':
        if entry.bowel_movements:
            bowel = entry.bowel_movements[0]
            data['bowel'] = {
                'bristol_type': bowel.bristol_type,
                'urgency': bowel.urgency,
                'completeness': bowel.completeness,
                'straining': bowel.straining,
                'blood_present': bowel.blood_present,
                'mucus_present': bowel.mucus_present,
                'color': bowel.color,
                'notes': bowel.notes
            }

    elif entry.entry_type == 'stress':
        if entry.stress_logs:
            stress = entry.stress_logs[0]
            data['stress'] = {
                'stress_level': stress.stress_level,
                'stress_types': stress.stress_types,
                'physical_symptoms': stress.physical_symptoms,
                'management_actions': stress.management_actions,
                'duration_status': stress.duration_status,
                'notes': stress.notes
            }

    elif entry.entry_type == 'note':
        if entry.notes:
            note = entry.notes[0]
            data['note'] = {
                'category': note.category,
                'title': note.title,
                'content': note.content,
                'mood': note.mood,
                'tags': note.tags
            }

    return data


@bp.route('/diary/entries', methods=['GET'])
@require_api_key
@require_scope('read:diary')
def get_diary_entries():
    """
    Get diary entries for a specific month
    Query params: year (int), month (int)
    Returns entries grouped by date with monthly statistics
    """
    try:
        today = date.today()
        year_param = request.args.get('year', today.year)
        month_param = request.args.get('month', today.month)

        # Validate year and month
        try:
            year, month = validate_year_month(year_param, month_param)
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400

        # Get entries for the specified month
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)

        # Use eager loading to prevent N+1 queries
        entries = DiaryEntry.query.options(
            joinedload(DiaryEntry.meals).joinedload(Meal.meal_foods).joinedload(MealFood.food),
            joinedload(DiaryEntry.symptoms),
            joinedload(DiaryEntry.bowel_movements),
            joinedload(DiaryEntry.stress_logs),
            joinedload(DiaryEntry.notes)
        ).filter(
            DiaryEntry.entry_date >= start_date,
            DiaryEntry.entry_date < end_date
        ).order_by(DiaryEntry.entry_date, DiaryEntry.entry_time).all()

        # Group entries by date
        entries_by_date = defaultdict(list)
        for entry in entries:
            date_str = entry.entry_date.isoformat()
            entries_by_date[date_str].append(serialize_diary_entry(entry))

        # Calculate monthly statistics
        month_stats = {
            'meals': len([e for e in entries if e.entry_type == 'meal']),
            'symptoms': len([e for e in entries if e.entry_type == 'symptom']),
            'bowel': len([e for e in entries if e.entry_type == 'bowel']),
            'stress': len([e for e in entries if e.entry_type == 'stress']),
            'notes': len([e for e in entries if e.entry_type == 'note']),
            'total': len(entries)
        }

        return jsonify({
            'year': year,
            'month': month,
            'entries_by_date': dict(entries_by_date),
            'statistics': month_stats
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/diary/day/<date_string>', methods=['GET'])
@require_api_key
@require_scope('read:diary')
def get_day_entries(date_string):
    """
    Get all entries for a specific date with nutrition totals
    Path param: date_string (YYYY-MM-DD)
    Returns entries and daily nutrition breakdown
    """
    try:
        # Validate and parse date
        try:
            validate_date_string(date_string, 'date')
            entry_date = datetime.strptime(date_string, '%Y-%m-%d').date()
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400

        # Get all entries for this date (with eager loading)
        entries = DiaryEntry.query.options(
            joinedload(DiaryEntry.meals).joinedload(Meal.meal_foods).joinedload(MealFood.food),
            joinedload(DiaryEntry.symptoms),
            joinedload(DiaryEntry.bowel_movements),
            joinedload(DiaryEntry.stress_logs),
            joinedload(DiaryEntry.notes)
        ).filter_by(
            entry_date=entry_date
        ).order_by(DiaryEntry.entry_time).all()

        # Serialize entries
        serialized_entries = [serialize_diary_entry(e) for e in entries]

        # Calculate daily nutrition totals from meals
        daily_nutrition = {
            'energy_kj': 0,
            'protein_g': 0,
            'fat_g': 0,
            'carbs_g': 0,
            'sodium_mg': 0
        }

        meal_entries = [e for e in entries if e.entry_type == 'meal']
        for entry in meal_entries:
            for meal in entry.meals:
                for meal_food in meal.meal_foods:
                    daily_nutrition['energy_kj'] += meal_food.energy_kj or 0
                    daily_nutrition['protein_g'] += meal_food.protein_g or 0
                    daily_nutrition['fat_g'] += meal_food.fat_g or 0
                    daily_nutrition['carbs_g'] += meal_food.carbs_g or 0
                    daily_nutrition['sodium_mg'] += meal_food.sodium_mg or 0

        # Round nutrition values
        for key in daily_nutrition:
            daily_nutrition[key] = round(daily_nutrition[key], 1)

        return jsonify({
            'date': date_string,
            'entries': serialized_entries,
            'nutrition': daily_nutrition,
            'entry_count': len(entries)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/diary/trends', methods=['GET'])
@require_api_key
@require_scope('read:diary')
def get_diary_trends():
    """
    Get symptom trends over a specified number of days
    Query param: days (int, default 30)
    Returns time-series symptom data and averages
    """
    try:
        # Validate days parameter
        try:
            days = validate_optional_int(
                request.args.get('days'),
                field_name='days',
                min_val=1,
                max_val=365,
                default=30
            )
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400

        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)

        # Get symptom entries in date range
        symptom_entries = DiaryEntry.query.filter(
            DiaryEntry.entry_type == 'symptom',
            DiaryEntry.entry_date >= start_date,
            DiaryEntry.entry_date <= end_date
        ).order_by(DiaryEntry.entry_date).all()

        # Build time-series data
        symptom_data = []
        symptom_types = ['bloating', 'pain', 'wind', 'nausea', 'heartburn',
                        'headache', 'brain_fog', 'fatigue', 'sinus_issues']

        for entry in symptom_entries:
            if entry.symptoms:
                symptom = entry.symptoms[0]
                data_point = {
                    'date': entry.entry_date.isoformat(),
                    'time': entry.entry_time.strftime('%H:%M') if entry.entry_time else None
                }
                for symptom_type in symptom_types:
                    data_point[symptom_type] = getattr(symptom, symptom_type, 0)
                symptom_data.append(data_point)

        # Calculate averages
        if symptom_data:
            averages = {}
            for symptom_type in symptom_types:
                values = [s[symptom_type] for s in symptom_data if s[symptom_type] is not None]
                averages[symptom_type] = round(sum(values) / len(values), 1) if values else 0
        else:
            averages = {s: 0 for s in symptom_types}

        return jsonify({
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'days': days,
            'symptom_data': symptom_data,
            'averages': averages,
            'total_entries': len(symptom_data)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/diary/weekly', methods=['GET'])
@require_api_key
@require_scope('read:diary')
def get_weekly_summary():
    """
    Get weekly summary of diary entries
    Query param: start_date (YYYY-MM-DD, defaults to current week)
    Returns daily entry counts and weekly totals
    """
    try:
        # Get start date from query or use current week
        start_date_str = request.args.get('start_date')
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        else:
            # Default to start of current week (Monday)
            today = date.today()
            start_date = today - timedelta(days=today.weekday())

        # Calculate end date (Sunday)
        end_date = start_date + timedelta(days=6)

        # Get all entries for the week
        entries = DiaryEntry.query.filter(
            DiaryEntry.entry_date >= start_date,
            DiaryEntry.entry_date <= end_date
        ).all()

        # Group entries by date and type
        daily_counts = defaultdict(lambda: {'meals': 0, 'symptoms': 0, 'bowel': 0, 'stress': 0, 'notes': 0, 'total': 0})

        for entry in entries:
            date_str = entry.entry_date.isoformat()
            daily_counts[date_str][entry.entry_type + 's'] = daily_counts[date_str].get(entry.entry_type + 's', 0) + 1
            daily_counts[date_str]['total'] += 1

        # Build weekly data with all 7 days
        weekly_data = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.isoformat()
            weekly_data.append({
                'date': date_str,
                'day_name': current_date.strftime('%A'),
                'counts': daily_counts.get(date_str, {'meals': 0, 'symptoms': 0, 'bowel': 0, 'stress': 0, 'notes': 0, 'total': 0})
            })
            current_date += timedelta(days=1)

        # Calculate weekly totals
        weekly_totals = {
            'meals': sum(day['counts']['meals'] for day in weekly_data),
            'symptoms': sum(day['counts']['symptoms'] for day in weekly_data),
            'bowel': sum(day['counts']['bowel'] for day in weekly_data),
            'stress': sum(day['counts']['stress'] for day in weekly_data),
            'notes': sum(day['counts']['notes'] for day in weekly_data),
            'total': len(entries)
        }

        return jsonify({
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'weekly_data': weekly_data,
            'weekly_totals': weekly_totals
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# CRUD ENDPOINTS - Create, Update, Delete
# ============================================================================

# Meal Endpoints
@bp.route('/diary/meals', methods=['POST'])
@require_api_key
@require_scope('write:diary')
def diary_create_meal():
    """
    Create a new meal entry
    Body: {
        entry_date: "YYYY-MM-DD",
        entry_time: "HH:MM",
        meal_type: "Breakfast|Lunch|Dinner|Snack",
        location: "Home|Restaurant|Work|Other",
        preparation: "Fresh|Cooked|Processed|Raw",
        notes: "optional text",
        foods: [{food_id: int, portion_size: "150g", serving_type: "safe|moderate|high"}],
        recipe_id: int (optional),
        saved_meal_id: int (optional)
    }
    """
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('entry_date'):
            return jsonify({'error': 'entry_date is required'}), 400
        if not data.get('meal_type'):
            return jsonify({'error': 'meal_type is required'}), 400
        if not data.get('foods') and not data.get('recipe_id') and not data.get('saved_meal_id'):
            return jsonify({'error': 'Must provide foods, recipe_id, or saved_meal_id'}), 400

        # Parse dates
        try:
            entry_date = datetime.strptime(data['entry_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid entry_date format. Use YYYY-MM-DD'}), 400

        entry_time = None
        if data.get('entry_time'):
            try:
                entry_time = datetime.strptime(data['entry_time'], '%H:%M').time()
            except ValueError:
                return jsonify({'error': 'Invalid entry_time format. Use HH:MM'}), 400

        # Get foods list (from direct input, recipe, or saved meal)
        foods_data = data.get('foods', [])
        recipe_id = data.get('recipe_id')
        saved_meal_id = data.get('saved_meal_id')

        if recipe_id:
            recipe = Recipe.query.get(recipe_id)
            if not recipe:
                return jsonify({'error': 'Recipe not found'}), 404
            foods_data = [{'food_id': ing.food_id, 'portion_size': ing.quantity or ''}
                         for ing in recipe.ingredients]
        elif saved_meal_id:
            saved_meal = SavedMeal.query.get(saved_meal_id)
            if not saved_meal:
                return jsonify({'error': 'Saved meal not found'}), 404
            foods_data = [{'food_id': item.food_id, 'portion_size': item.portion_size or ''}
                         for item in saved_meal.meal_items]
            recipe_id = None

        # Create diary entry
        diary_entry = DiaryEntry(
            entry_date=entry_date,
            entry_time=entry_time,
            entry_type='meal'
        )
        db.session.add(diary_entry)
        db.session.flush()

        # Create meal
        meal = Meal(
            diary_entry_id=diary_entry.id,
            meal_type=data['meal_type'],
            location=data.get('location', 'Home'),
            preparation=data.get('preparation', 'Fresh'),
            notes=data.get('notes', ''),
            recipe_id=recipe_id
        )
        db.session.add(meal)
        db.session.flush()

        # Add foods to meal
        for food_data in foods_data:
            if food_data.get('food_id'):
                food = Food.query.get(food_data['food_id'])
                if not food:
                    db.session.rollback()
                    return jsonify({'error': f'Food {food_data["food_id"]} not found'}), 404

                nutrition = parse_portion_and_calculate_nutrition(
                    food_data.get('portion_size', ''),
                    food
                )

                meal_food = MealFood(
                    meal_id=meal.id,
                    food_id=food.id,
                    portion_size=food_data.get('portion_size', ''),
                    serving_type=food_data.get('serving_type'),
                    num_servings=nutrition['num_servings'],
                    energy_kj=nutrition['energy_kj'],
                    protein_g=nutrition['protein_g'],
                    fat_g=nutrition['fat_g'],
                    carbs_g=nutrition['carbs_g'],
                    sodium_mg=nutrition['sodium_mg']
                )
                db.session.add(meal_food)

        db.session.commit()

        return jsonify({
            'id': diary_entry.id,
            'message': 'Meal created successfully'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/diary/meals/<int:entry_id>', methods=['PUT'])
@require_api_key
@require_scope('write:diary')
def diary_update_meal(entry_id):
    """Update an existing meal entry"""
    try:
        entry = DiaryEntry.query.get(entry_id)
        if not entry or entry.entry_type != 'meal':
            return jsonify({'error': 'Meal entry not found'}), 404

        meal = entry.meals[0] if entry.meals else None
        if not meal:
            return jsonify({'error': 'Meal data not found'}), 404

        data = request.get_json()

        # Update entry date/time if provided
        if data.get('entry_date'):
            try:
                entry.entry_date = datetime.strptime(data['entry_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid entry_date format'}), 400

        if data.get('entry_time'):
            try:
                entry.entry_time = datetime.strptime(data['entry_time'], '%H:%M').time()
            except ValueError:
                return jsonify({'error': 'Invalid entry_time format'}), 400

        # Update meal details
        if data.get('meal_type'):
            meal.meal_type = data['meal_type']
        if 'location' in data:
            meal.location = data['location']
        if 'preparation' in data:
            meal.preparation = data['preparation']
        if 'notes' in data:
            meal.notes = data['notes']
        if 'recipe_id' in data:
            meal.recipe_id = data['recipe_id']

        # Update foods if provided
        if 'foods' in data:
            # Delete old meal foods
            MealFood.query.filter_by(meal_id=meal.id).delete()

            # Add new foods
            for food_data in data['foods']:
                if food_data.get('food_id'):
                    food = Food.query.get(food_data['food_id'])
                    if not food:
                        db.session.rollback()
                        return jsonify({'error': f'Food {food_data["food_id"]} not found'}), 404

                    nutrition = parse_portion_and_calculate_nutrition(
                        food_data.get('portion_size', ''),
                        food
                    )

                    meal_food = MealFood(
                        meal_id=meal.id,
                        food_id=food.id,
                        portion_size=food_data.get('portion_size', ''),
                        serving_type=food_data.get('serving_type'),
                        num_servings=nutrition['num_servings'],
                        energy_kj=nutrition['energy_kj'],
                        protein_g=nutrition['protein_g'],
                        fat_g=nutrition['fat_g'],
                        carbs_g=nutrition['carbs_g'],
                        sodium_mg=nutrition['sodium_mg']
                    )
                    db.session.add(meal_food)

        db.session.commit()

        return jsonify({
            'success': True,
            'meal_id': meal.id,
            'message': 'Meal updated successfully!'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# =============================================================================
# PHASE 3: BATCH OPERATIONS ENDPOINT
# =============================================================================

@bp.route('/diary/entries/bulk', methods=['POST'])
@require_api_key
@require_scope('write:diary')
def create_bulk_entries():
    """
    POST /api/v1/diary/entries/bulk
    Create multiple diary entries in one API call (multiple types)

    Expected JSON:
    {
        "entries": [
            {
                "type": "meal",
                "date": "2026-02-12",
                "data": {
                    "meal_type": "Breakfast",
                    "foods": [...],
                    ...
                }
            },
            {
                "type": "symptom",
                "date": "2026-02-12",
                "data": {
                    "symptom_type": "bloating",
                    "severity": 5,
                    ...
                }
            },
            ...
        ]
    }

    Returns:
    {
        "success": true,
        "created_count": 3,
        "results": [
            {"type": "meal", "id": 123, "success": true},
            {"type": "symptom", "id": 124, "success": true},
            {"type": "note", "error": "Invalid data", "success": false}
        ]
    }
    """
    try:
        data = request.get_json()
        if not data or 'entries' not in data:
            return jsonify({'error': 'entries array is required'}), 400

        # Validate entries array
        try:
            entries = validate_array_size(
                data['entries'],
                field_name='entries',
                min_size=1,
                max_size=50
            )
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400

        results = []
        created_count = 0

        for idx, entry_data in enumerate(entries):
            entry_type = entry_data.get('type')
            entry_date_str = entry_data.get('date')
            data_obj = entry_data.get('data', {})

            # Validate required fields
            if not entry_type:
                results.append({
                    'index': idx,
                    'type': entry_type,
                    'success': False,
                    'error': 'type is required'
                })
                continue

            if not entry_date_str:
                results.append({
                    'index': idx,
                    'type': entry_type,
                    'success': False,
                    'error': 'date is required'
                })
                continue

            try:
                entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d').date()
            except ValueError:
                results.append({
                    'index': idx,
                    'type': entry_type,
                    'success': False,
                    'error': 'Invalid date format (use YYYY-MM-DD)'
                })
                continue

            try:
                # Create diary entry based on type
                if entry_type == 'meal':
                    # Create meal entry
                    diary_entry = DiaryEntry(
                        entry_date=entry_date,
                        entry_type='meal'
                    )
                    db.session.add(diary_entry)
                    db.session.flush()

                    meal = Meal(
                        diary_entry_id=diary_entry.id,
                        meal_type=data_obj.get('meal_type'),
                        location=data_obj.get('location'),
                        preparation=data_obj.get('preparation'),
                        recipe_id=data_obj.get('recipe_id'),
                        notes=data_obj.get('notes')
                    )
                    db.session.add(meal)
                    db.session.flush()

                    # Add foods
                    if 'foods' in data_obj:
                        for food_data in data_obj['foods']:
                            food = Food.query.get(food_data.get('food_id'))
                            if food:
                                nutrition = parse_portion_and_calculate_nutrition(
                                    food_data.get('portion_size', ''),
                                    food
                                )
                                meal_food = MealFood(
                                    meal_id=meal.id,
                                    food_id=food.id,
                                    portion_size=food_data.get('portion_size'),
                                    serving_type=food_data.get('serving_type'),
                                    num_servings=nutrition['num_servings'],
                                    energy_kj=nutrition['energy_kj'],
                                    protein_g=nutrition['protein_g'],
                                    fat_g=nutrition['fat_g'],
                                    carbs_g=nutrition['carbs_g'],
                                    sodium_mg=nutrition['sodium_mg']
                                )
                                db.session.add(meal_food)

                    results.append({
                        'index': idx,
                        'type': entry_type,
                        'id': diary_entry.id,
                        'meal_id': meal.id,
                        'success': True
                    })
                    created_count += 1

                elif entry_type == 'symptom':
                    # Create symptom entry
                    diary_entry = DiaryEntry(
                        entry_date=entry_date,
                        entry_type='symptom'
                    )
                    db.session.add(diary_entry)
                    db.session.flush()

                    symptom = Symptom(
                        diary_entry_id=diary_entry.id,
                        bloating=data_obj.get('bloating', 0),
                        pain=data_obj.get('pain', 0),
                        wind=data_obj.get('wind', 0),
                        nausea=data_obj.get('nausea', 0),
                        heartburn=data_obj.get('heartburn', 0),
                        headache=data_obj.get('headache', 0),
                        brain_fog=data_obj.get('brain_fog', 0),
                        fatigue=data_obj.get('fatigue', 0),
                        sinus_issues=data_obj.get('sinus_issues', 0),
                        severity=data_obj.get('severity'),
                        duration=data_obj.get('duration'),
                        notes=data_obj.get('notes')
                    )
                    db.session.add(symptom)

                    results.append({
                        'index': idx,
                        'type': entry_type,
                        'id': diary_entry.id,
                        'symptom_id': symptom.id,
                        'success': True
                    })
                    created_count += 1

                elif entry_type == 'bowel':
                    # Create bowel movement entry
                    diary_entry = DiaryEntry(
                        entry_date=entry_date,
                        entry_type='bowel'
                    )
                    db.session.add(diary_entry)
                    db.session.flush()

                    bowel = BowelMovement(
                        diary_entry_id=diary_entry.id,
                        bristol_type=data_obj.get('bristol_type'),
                        urgency=data_obj.get('urgency'),
                        completeness=data_obj.get('completeness'),
                        straining=data_obj.get('straining'),
                        blood_present=data_obj.get('blood_present'),
                        mucus_present=data_obj.get('mucus_present'),
                        color=data_obj.get('color'),
                        notes=data_obj.get('notes')
                    )
                    db.session.add(bowel)

                    results.append({
                        'index': idx,
                        'type': entry_type,
                        'id': diary_entry.id,
                        'bowel_id': bowel.id,
                        'success': True
                    })
                    created_count += 1

                elif entry_type == 'stress':
                    # Create stress log entry
                    diary_entry = DiaryEntry(
                        entry_date=entry_date,
                        entry_type='stress'
                    )
                    db.session.add(diary_entry)
                    db.session.flush()

                    stress = StressLog(
                        diary_entry_id=diary_entry.id,
                        stress_level=data_obj.get('stress_level'),
                        stress_types=data_obj.get('stress_types'),
                        physical_symptoms=data_obj.get('physical_symptoms'),
                        management_actions=data_obj.get('management_actions'),
                        duration_status=data_obj.get('duration_status'),
                        notes=data_obj.get('notes')
                    )
                    db.session.add(stress)

                    results.append({
                        'index': idx,
                        'type': entry_type,
                        'id': diary_entry.id,
                        'stress_id': stress.id,
                        'success': True
                    })
                    created_count += 1

                elif entry_type == 'note':
                    # Create general note entry
                    diary_entry = DiaryEntry(
                        entry_date=entry_date,
                        entry_type='note'
                    )
                    db.session.add(diary_entry)
                    db.session.flush()

                    note = Note(
                        diary_entry_id=diary_entry.id,
                        title=data_obj.get('title'),
                        content=data_obj.get('content')
                    )
                    db.session.add(note)

                    results.append({
                        'index': idx,
                        'type': entry_type,
                        'id': diary_entry.id,
                        'note_id': note.id,
                        'success': True
                    })
                    created_count += 1

                else:
                    results.append({
                        'index': idx,
                        'type': entry_type,
                        'success': False,
                        'error': f'Unknown entry type: {entry_type}'
                    })

            except Exception as entry_error:
                results.append({
                    'index': idx,
                    'type': entry_type,
                    'success': False,
                    'error': str(entry_error)
                })

        # Commit all successful entries
        db.session.commit()

        return jsonify({
            'success': True,
            'created_count': created_count,
            'total_requested': len(entries),
            'results': results
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# =============================================================================
# 2 NEW MEAL PLAN ENDPOINTS FOR APP2 INTEGRATION
# =============================================================================

@bp.route('/diary/meal-plan', methods=['POST'])
@require_api_key
@require_scope('write:diary')
def create_meal_plan():
    """
    POST /api/v1/diary/meal-plan
    Save a 7-day (or N-day) meal plan with nested days and meals
    Input: {
        "name": "Week 1 Low-FODMAP Plan",
        "start_date": "2026-01-06",
        "notes": "Optional notes",
        "days": [
            {
                "date": "2026-01-06",
                "meals": [
                    {"meal_type": "Breakfast", "recipe_id": 5},
                    {"meal_type": "Lunch", "food_id": 12, "custom_label": "Rice with chicken"},
                    {"meal_type": "Dinner", "saved_meal_id": 3}
                ]
            }
        ]
    }
    """
    try:
        from models.diary import MealPlan, MealPlanDay, MealPlanItem
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Request body required'}), 400

        name = data.get('name', '').strip()
        start_date_str = data.get('start_date')
        notes = data.get('notes', '')
        days_data = data.get('days', [])

        if not name:
            return jsonify({'error': 'name is required'}), 400
        if not start_date_str:
            return jsonify({'error': 'start_date is required'}), 400
        if not days_data:
            return jsonify({'error': 'days array is required and must not be empty'}), 400

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'start_date must be in YYYY-MM-DD format'}), 400

        # Calculate end date from number of days
        end_date = start_date + timedelta(days=len(days_data) - 1)

        # Create meal plan
        meal_plan = MealPlan(
            name=name,
            start_date=start_date,
            end_date=end_date,
            notes=notes
        )
        db.session.add(meal_plan)
        db.session.flush()  # Get the ID without committing

        # Create days and items
        days_count = 0
        for day_data in days_data:
            day_date_str = day_data.get('date')
            meals = day_data.get('meals', [])

            if not day_date_str:
                return jsonify({'error': 'Each day must have a date'}), 400

            try:
                day_date = datetime.strptime(day_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': f'Invalid date format: {day_date_str}. Use YYYY-MM-DD'}), 400

            meal_plan_day = MealPlanDay(
                plan_id=meal_plan.id,
                plan_date=day_date
            )
            db.session.add(meal_plan_day)
            db.session.flush()

            # Add meals for this day
            for meal_data in meals:
                meal_type = meal_data.get('meal_type')
                recipe_id = meal_data.get('recipe_id')
                saved_meal_id = meal_data.get('saved_meal_id')
                food_id = meal_data.get('food_id')
                custom_label = meal_data.get('custom_label')

                meal_plan_item = MealPlanItem(
                    day_id=meal_plan_day.id,
                    meal_type=meal_type,
                    recipe_id=recipe_id,
                    saved_meal_id=saved_meal_id,
                    food_id=food_id,
                    custom_label=custom_label
                )
                db.session.add(meal_plan_item)

            days_count += 1

        db.session.commit()

        return jsonify({
            'success': True,
            'plan_id': meal_plan.id,
            'name': meal_plan.name,
            'start_date': meal_plan.start_date.isoformat(),
            'end_date': meal_plan.end_date.isoformat(),
            'days_count': days_count,
            'message': 'Meal plan created successfully'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/diary/meal-plan/<int:plan_id>', methods=['GET'])
@require_api_key
@require_scope('read:diary')
def get_meal_plan(plan_id):
    """
    GET /api/v1/diary/meal-plan/<int:plan_id>
    Retrieve a saved meal plan with full detail (days and meals)
    """
    try:
        from models.diary import MealPlan

        plan = MealPlan.query.get(plan_id)
        if not plan:
            return jsonify({'error': f'Meal plan {plan_id} not found'}), 404

        # Build response with nested structure
        days_response = []
        for day in plan.days:
            meals_response = []
            for item in day.meals:
                meal_dict = {
                    'id': item.id,
                    'meal_type': item.meal_type,
                    'recipe_id': item.recipe_id,
                    'recipe_name': item.recipe.name if item.recipe else None,
                    'saved_meal_id': item.saved_meal_id,
                    'saved_meal_name': item.saved_meal.name if item.saved_meal else None,
                    'food_id': item.food_id,
                    'food_name': item.food.name if item.food else None,
                    'custom_label': item.custom_label
                }
                meals_response.append(meal_dict)

            days_response.append({
                'id': day.id,
                'plan_date': day.plan_date.isoformat(),
                'meals': meals_response
            })

        return jsonify({
            'plan_id': plan.id,
            'name': plan.name,
            'start_date': plan.start_date.isoformat(),
            'end_date': plan.end_date.isoformat(),
            'notes': plan.notes,
            'created_at': plan.created_at.isoformat() if plan.created_at else None,
            'days': days_response,
            'days_count': len(days_response)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
