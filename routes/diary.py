from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime, date, time, timedelta
import calendar
import re
from collections import defaultdict
from models.diary import DiaryEntry, Meal, MealFood, Symptom, BowelMovement, StressLog, Note
from models.food import Food
from models.recipe import Recipe, SavedMeal
from database import db

bp = Blueprint('diary', __name__, url_prefix='/diary')


def parse_portion_and_calculate_nutrition(portion_size, food):
    """
    Parse portion size string and calculate nutrition values.
    Returns dict with num_servings, energy_kj, protein_g, fat_g, carbs_g, sodium_mg

    Supported formats:
    - "2 servings", "1.5 serves", "1 serve" - multiply by per_serve values
    - "150g", "200 g" - calculate from per_100 values
    - "250ml", "300 ml" - calculate from per_100 values (treating ml as g)
    """
    result = {
        'num_servings': None,
        'energy_kj': None,
        'protein_g': None,
        'fat_g': None,
        'carbs_g': None,
        'sodium_mg': None
    }

    if not portion_size or not food:
        return result

    portion_lower = portion_size.lower().strip()

    # Try to extract number from the portion string
    number_match = re.search(r'(\d+\.?\d*)', portion_lower)
    if not number_match:
        # No number found, assume 1 serving
        multiplier = 1.0
        use_per_serve = True
    else:
        num_value = float(number_match.group(1))

        # Check if it's servings
        if 'serv' in portion_lower:
            multiplier = num_value
            use_per_serve = True
            result['num_servings'] = multiplier
        # Check if it's grams
        elif 'g' in portion_lower and 'mg' not in portion_lower:
            # Calculate based on per 100g
            multiplier = num_value / 100.0
            use_per_serve = False
        # Check if it's ml
        elif 'ml' in portion_lower:
            # Treat ml same as g for calculation
            multiplier = num_value / 100.0
            use_per_serve = False
        else:
            # Default: assume it's number of servings
            multiplier = num_value
            use_per_serve = True
            result['num_servings'] = multiplier

    # Calculate nutrition based on multiplier
    if use_per_serve:
        # Use per_serve values
        if food.energy_per_serve_kj is not None:
            result['energy_kj'] = round(food.energy_per_serve_kj * multiplier, 1)
        if food.protein_per_serve is not None:
            result['protein_g'] = round(food.protein_per_serve * multiplier, 1)
        if food.fat_per_serve is not None:
            result['fat_g'] = round(food.fat_per_serve * multiplier, 1)
        if food.carbohydrate_per_serve is not None:
            result['carbs_g'] = round(food.carbohydrate_per_serve * multiplier, 1)
        if food.sodium_per_serve is not None:
            result['sodium_mg'] = round(food.sodium_per_serve * multiplier, 1)
    else:
        # Use per_100 values
        if food.energy_per_100_kj is not None:
            result['energy_kj'] = round(food.energy_per_100_kj * multiplier, 1)
        if food.protein_per_100 is not None:
            result['protein_g'] = round(food.protein_per_100 * multiplier, 1)
        if food.fat_per_100 is not None:
            result['fat_g'] = round(food.fat_per_100 * multiplier, 1)
        if food.carbohydrate_per_100 is not None:
            result['carbs_g'] = round(food.carbohydrate_per_100 * multiplier, 1)
        if food.sodium_per_100 is not None:
            result['sodium_mg'] = round(food.sodium_per_100 * multiplier, 1)

    return result


def entry_has_content(entry):
    """Check if a diary entry has actual content (not orphaned)"""
    if entry.entry_type == 'meal':
        return len(entry.meals) > 0
    elif entry.entry_type == 'symptom':
        return len(entry.symptoms) > 0
    elif entry.entry_type == 'bowel':
        return len(entry.bowel_movements) > 0
    elif entry.entry_type == 'stress':
        return len(entry.stress_logs) > 0
    elif entry.entry_type == 'note':
        return len(entry.notes) > 0
    return False

@bp.route('/')
def index():
    """Diary calendar view"""
    today = date.today()

    # Get year and month from query parameters or use current
    year = request.args.get('year', today.year, type=int)
    month = request.args.get('month', today.month, type=int)

    current_date = date(year, month, 1)

    # Calculate previous and next months
    if month == 1:
        prev_month = date(year - 1, 12, 1)
    else:
        prev_month = date(year, month - 1, 1)

    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)

    # Get all diary entries for the current month (and a bit before/after for calendar display)
    # Get entries from the month before to the month after to cover all visible days
    start_date = prev_month
    end_date = next_month + timedelta(days=31)

    all_entries = DiaryEntry.query.filter(
        DiaryEntry.entry_date >= start_date,
        DiaryEntry.entry_date < end_date
    ).all()

    # Filter out and delete orphaned entries (entries with no actual content)
    entries = []
    for entry in all_entries:
        if entry_has_content(entry):
            entries.append(entry)
        else:
            # Auto-delete orphaned entries
            db.session.delete(entry)

    # Commit any orphaned entry deletions
    if len(entries) != len(all_entries):
        db.session.commit()

    # Group entries by date
    entries_by_date = defaultdict(list)
    for entry in entries:
        entries_by_date[entry.entry_date.isoformat()].append(entry)

    # Generate calendar weeks
    cal = calendar.monthcalendar(year, month)
    calendar_weeks = []

    for week in cal:
        week_dates = []
        for day in week:
            if day == 0:
                week_dates.append(None)
            else:
                week_dates.append(date(year, month, day))
        calendar_weeks.append(week_dates)

    # Calculate month statistics
    month_entries = [e for e in entries if e.entry_date.month == month and e.entry_date.year == year]
    month_stats = {
        'meals': len([e for e in month_entries if e.entry_type == 'meal']),
        'symptoms': len([e for e in month_entries if e.entry_type == 'symptom']),
        'bowel': len([e for e in month_entries if e.entry_type == 'bowel']),
        'stress': len([e for e in month_entries if e.entry_type == 'stress']),
        'notes': len([e for e in month_entries if e.entry_type == 'note']),
        'total': len(month_entries)
    }

    return render_template('diary/calendar.html',
                         current_date=current_date,
                         today=today,
                         prev_month=prev_month,
                         next_month=next_month,
                         calendar_weeks=calendar_weeks,
                         entries_by_date=entries_by_date,
                         month_stats=month_stats)

@bp.route('/day/<date_string>')
def day_view(date_string):
    """Single day view with all entries"""
    try:
        entry_date = datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format', 'error')
        return redirect(url_for('diary.index'))

    all_entries = DiaryEntry.query.filter_by(entry_date=entry_date).order_by(DiaryEntry.entry_time).all()

    # Filter out and delete orphaned entries (entries with no actual content)
    entries = []
    for entry in all_entries:
        if entry_has_content(entry):
            entries.append(entry)
        else:
            # Auto-delete orphaned entries
            db.session.delete(entry)

    # Commit any deletions
    if len(entries) != len(all_entries):
        db.session.commit()

    return render_template('diary/day.html',
                         entry_date=entry_date,
                         entries=entries,
                         timedelta=timedelta)

@bp.route('/add/meal', methods=['GET', 'POST'])
def add_meal():
    """Add or edit meal entry"""
    edit_param = request.args.get('edit', '')
    existing_entry = None
    existing_meal = None
    edit_entry_ids = []
    all_existing_entries = []

    # Parse edit parameter - can be single ID or comma-separated list
    if edit_param:
        try:
            edit_entry_ids = [int(id.strip()) for id in edit_param.split(',') if id.strip()]
        except ValueError:
            edit_entry_ids = []

    # Load existing entries for editing
    if edit_entry_ids:
        for entry_id in edit_entry_ids:
            entry = DiaryEntry.query.get(entry_id)
            if entry and entry.entry_type == 'meal' and entry.meals:
                all_existing_entries.append(entry)

        # Use first entry as the primary entry for form defaults
        if all_existing_entries:
            existing_entry = all_existing_entries[0]
            existing_meal = existing_entry.meals[0]

    if request.method == 'POST':
        try:
            # Get form data
            meal_date = datetime.strptime(request.form.get('meal_date'), '%Y-%m-%d').date()
            meal_time = datetime.strptime(request.form.get('meal_time'), '%H:%M').time()
            meal_type = request.form.get('meal_type')
            location = request.form.get('location', 'Home')
            preparation = request.form.get('preparation', 'Fresh')
            notes = request.form.get('notes', '')

            # Check source type (individual foods, recipe, or saved meal)
            source_type = request.form.get('source_type', 'foods')
            recipe_id = request.form.get('recipe_id', type=int)
            saved_meal_id = request.form.get('saved_meal_id', type=int)

            # Get selected foods (will be populated differently based on source)
            food_ids = request.form.getlist('food_ids[]')
            portions = request.form.getlist('portions[]')
            serving_types = request.form.getlist('serving_types[]')

            # If recipe selected, get foods from recipe
            if source_type == 'recipe' and recipe_id:
                recipe = Recipe.query.get_or_404(recipe_id)
                food_ids = [str(ing.food_id) for ing in recipe.ingredients]
                portions = [ing.quantity or '' for ing in recipe.ingredients]
                serving_types = ['' for _ in recipe.ingredients]  # No serving type for recipes

            # If saved meal selected, get foods from saved meal
            elif source_type == 'saved_meal' and saved_meal_id:
                saved_meal = SavedMeal.query.get_or_404(saved_meal_id)
                food_ids = [str(item.food_id) for item in saved_meal.meal_items]
                portions = [item.portion_size or '' for item in saved_meal.meal_items]
                serving_types = ['' for _ in saved_meal.meal_items]  # No serving type for saved meals
                recipe_id = None  # Saved meals don't link to recipes

            # Ensure serving_types list matches food_ids length
            while len(serving_types) < len(food_ids):
                serving_types.append('')

            if edit_entry_ids and existing_entry:
                # Update existing entry (first one)
                existing_entry.entry_date = meal_date
                existing_entry.entry_time = meal_time

                # Update meal
                existing_meal.meal_type = meal_type
                existing_meal.location = location
                existing_meal.preparation = preparation
                existing_meal.notes = notes
                if source_type == 'recipe' and recipe_id:
                    existing_meal.recipe_id = recipe_id
                else:
                    existing_meal.recipe_id = None

                # Delete old meal foods and add new ones
                MealFood.query.filter_by(meal_id=existing_meal.id).delete()

                # Add new foods
                for food_id, portion, serving_type in zip(food_ids, portions, serving_types):
                    if food_id:
                        # Get food for nutrition calculation
                        food_obj = Food.query.get(int(food_id))
                        nutrition = parse_portion_and_calculate_nutrition(portion, food_obj)

                        meal_food = MealFood(
                            meal_id=existing_meal.id,
                            food_id=int(food_id),
                            portion_size=portion,
                            serving_type=serving_type if serving_type else None,
                            num_servings=nutrition['num_servings'],
                            energy_kj=nutrition['energy_kj'],
                            protein_g=nutrition['protein_g'],
                            fat_g=nutrition['fat_g'],
                            carbs_g=nutrition['carbs_g'],
                            sodium_mg=nutrition['sodium_mg']
                        )
                        db.session.add(meal_food)

                # Delete additional entries that were merged (if editing multiple)
                for extra_entry in all_existing_entries[1:]:
                    # Delete meal foods first
                    for meal in extra_entry.meals:
                        MealFood.query.filter_by(meal_id=meal.id).delete()
                    # Delete meals
                    Meal.query.filter_by(diary_entry_id=extra_entry.id).delete()
                    # Delete entry
                    db.session.delete(extra_entry)

                db.session.commit()
                flash(f'{meal_type} updated successfully!', 'success')
            else:
                # Create new entry
                diary_entry = DiaryEntry(
                    entry_date=meal_date,
                    entry_time=meal_time,
                    entry_type='meal'
                )
                db.session.add(diary_entry)
                db.session.flush()

                # Create meal
                meal = Meal(
                    diary_entry_id=diary_entry.id,
                    meal_type=meal_type,
                    location=location,
                    preparation=preparation,
                    notes=notes,
                    recipe_id=recipe_id if source_type == 'recipe' and recipe_id else None
                )
                db.session.add(meal)
                db.session.flush()

                # Add foods to meal
                for food_id, portion, serving_type in zip(food_ids, portions, serving_types):
                    if food_id:
                        # Get food for nutrition calculation
                        food_obj = Food.query.get(int(food_id))
                        nutrition = parse_portion_and_calculate_nutrition(portion, food_obj)

                        meal_food = MealFood(
                            meal_id=meal.id,
                            food_id=int(food_id),
                            portion_size=portion,
                            serving_type=serving_type if serving_type else None,
                            num_servings=nutrition['num_servings'],
                            energy_kj=nutrition['energy_kj'],
                            protein_g=nutrition['protein_g'],
                            fat_g=nutrition['fat_g'],
                            carbs_g=nutrition['carbs_g'],
                            sodium_mg=nutrition['sodium_mg']
                        )
                        db.session.add(meal_food)

                db.session.commit()
                flash(f'{meal_type} logged successfully!', 'success')

            return redirect(url_for('diary.day_view', date_string=meal_date.strftime('%Y-%m-%d')))

        except Exception as e:
            db.session.rollback()
            flash(f'Error saving meal: {str(e)}', 'error')
            return redirect(url_for('diary.add_meal'))

    # GET request - show form
    foods = Food.query.order_by(Food.name).all()
    recipes = Recipe.query.order_by(Recipe.name).all()
    saved_meals = SavedMeal.query.order_by(SavedMeal.name).all()

    # Convert to dictionaries for JSON serialization in template
    foods_dict = [food.to_dict() for food in foods]
    recipes_dict = [{'id': r.id, 'name': r.name, 'category': r.category} for r in recipes]
    saved_meals_dict = [{'id': sm.id, 'name': sm.name, 'meal_type': sm.meal_type} for sm in saved_meals]

    # Convert existing meal foods if editing (collect from all grouped entries)
    existing_meal_foods_dict = []
    if all_existing_entries:
        for entry in all_existing_entries:
            for meal in entry.meals:
                for mf in meal.meal_foods:
                    existing_meal_foods_dict.append({
                        'food_id': mf.food_id,
                        'portion_size': mf.portion_size,
                        'serving_type': mf.serving_type,
                        'food': mf.food.to_dict() if mf.food else None
                    })
    elif existing_meal:
        for mf in existing_meal.meal_foods:
            existing_meal_foods_dict.append({
                'food_id': mf.food_id,
                'portion_size': mf.portion_size,
                'serving_type': mf.serving_type,
                'food': mf.food.to_dict() if mf.food else None
            })

    return render_template('diary/entry-meal.html',
                         foods=foods_dict,
                         recipes=recipes_dict,
                         saved_meals=saved_meals_dict,
                         existing_meal_foods=existing_meal_foods_dict,
                         today=date.today(),
                         existing_entry=existing_entry,
                         existing_meal=existing_meal)

@bp.route('/add/symptom', methods=['GET', 'POST'])
def add_symptom():
    """Add or edit symptom entry"""
    edit_entry_id = request.args.get('edit', type=int)
    existing_entry = None
    existing_symptom = None

    # Load existing entry for editing
    if edit_entry_id:
        existing_entry = DiaryEntry.query.get_or_404(edit_entry_id)
        if existing_entry.entry_type == 'symptom' and existing_entry.symptoms:
            existing_symptom = existing_entry.symptoms[0]

    if request.method == 'POST':
        try:
            # Get form data
            symptom_date = datetime.strptime(request.form.get('symptom_date'), '%Y-%m-%d').date()
            symptom_time = datetime.strptime(request.form.get('symptom_time'), '%H:%M').time()

            if edit_entry_id and existing_entry:
                # Update existing entry
                existing_entry.entry_date = symptom_date
                existing_entry.entry_time = symptom_time

                # Update symptom
                existing_symptom.bloating = int(request.form.get('bloating', 0))
                existing_symptom.pain = int(request.form.get('pain', 0))
                existing_symptom.wind = int(request.form.get('wind', 0))
                existing_symptom.nausea = int(request.form.get('nausea', 0))
                existing_symptom.heartburn = int(request.form.get('heartburn', 0))
                existing_symptom.headache = int(request.form.get('headache', 0))
                existing_symptom.brain_fog = int(request.form.get('brain_fog', 0))
                existing_symptom.fatigue = int(request.form.get('fatigue', 0))
                existing_symptom.sinus_issues = int(request.form.get('sinus_issues', 0))
                existing_symptom.severity = request.form.get('severity')
                existing_symptom.duration = request.form.get('duration')
                existing_symptom.notes = request.form.get('notes', '')

                db.session.commit()
                flash('Symptom entry updated successfully!', 'success')
            else:
                # Create new diary entry
                diary_entry = DiaryEntry(
                    entry_date=symptom_date,
                    entry_time=symptom_time,
                    entry_type='symptom'
                )
                db.session.add(diary_entry)
                db.session.flush()

                # Create symptom
                symptom = Symptom(
                    diary_entry_id=diary_entry.id,
                    bloating=int(request.form.get('bloating', 0)),
                    pain=int(request.form.get('pain', 0)),
                    wind=int(request.form.get('wind', 0)),
                    nausea=int(request.form.get('nausea', 0)),
                    heartburn=int(request.form.get('heartburn', 0)),
                    headache=int(request.form.get('headache', 0)),
                    brain_fog=int(request.form.get('brain_fog', 0)),
                    fatigue=int(request.form.get('fatigue', 0)),
                    sinus_issues=int(request.form.get('sinus_issues', 0)),
                    severity=request.form.get('severity'),
                    duration=request.form.get('duration'),
                    notes=request.form.get('notes', '')
                )
                db.session.add(symptom)
                db.session.commit()
                flash('Symptoms logged successfully!', 'success')

            return redirect(url_for('diary.day_view', date_string=symptom_date.strftime('%Y-%m-%d')))

        except Exception as e:
            db.session.rollback()
            flash(f'Error saving symptom: {str(e)}', 'error')
            return redirect(url_for('diary.add_symptom'))

    return render_template('diary/entry-symptom.html',
                         today=date.today(),
                         existing_entry=existing_entry,
                         existing_symptom=existing_symptom)

@bp.route('/add/bowel', methods=['GET', 'POST'])
def add_bowel():
    """Add or edit bowel movement entry"""
    edit_entry_id = request.args.get('edit', type=int)
    existing_entry = None
    existing_bowel = None

    # Load existing entry for editing
    if edit_entry_id:
        existing_entry = DiaryEntry.query.get_or_404(edit_entry_id)
        if existing_entry.entry_type == 'bowel' and existing_entry.bowel_movements:
            existing_bowel = existing_entry.bowel_movements[0]

    if request.method == 'POST':
        try:
            # Get form data
            bowel_date = datetime.strptime(request.form.get('bowel_date'), '%Y-%m-%d').date()
            bowel_time = datetime.strptime(request.form.get('bowel_time'), '%H:%M').time()

            if edit_entry_id and existing_entry:
                # Update existing entry
                existing_entry.entry_date = bowel_date
                existing_entry.entry_time = bowel_time

                # Update bowel movement
                existing_bowel.bristol_type = int(request.form.get('bristol_type'))
                existing_bowel.urgency = request.form.get('urgency')
                existing_bowel.completeness = request.form.get('completeness')
                existing_bowel.straining = request.form.get('straining')
                existing_bowel.blood_present = request.form.get('blood_present') == 'on'
                existing_bowel.mucus_present = request.form.get('mucus_present') == 'on'
                existing_bowel.color = request.form.get('color')
                existing_bowel.notes = request.form.get('notes', '')

                db.session.commit()
                flash('Bowel movement updated successfully!', 'success')
            else:
                # Create new diary entry
                diary_entry = DiaryEntry(
                    entry_date=bowel_date,
                    entry_time=bowel_time,
                    entry_type='bowel'
                )
                db.session.add(diary_entry)
                db.session.flush()

                # Create bowel movement
                bowel = BowelMovement(
                    diary_entry_id=diary_entry.id,
                    bristol_type=int(request.form.get('bristol_type')),
                    urgency=request.form.get('urgency'),
                    completeness=request.form.get('completeness'),
                    straining=request.form.get('straining'),
                    blood_present=request.form.get('blood_present') == 'on',
                    mucus_present=request.form.get('mucus_present') == 'on',
                    color=request.form.get('color'),
                    notes=request.form.get('notes', '')
                )
                db.session.add(bowel)
                db.session.commit()
                flash('Bowel movement logged successfully!', 'success')

            return redirect(url_for('diary.day_view', date_string=bowel_date.strftime('%Y-%m-%d')))

        except Exception as e:
            db.session.rollback()
            flash(f'Error saving bowel movement: {str(e)}', 'error')
            return redirect(url_for('diary.add_bowel'))

    return render_template('diary/entry-bowel.html',
                         today=date.today(),
                         existing_entry=existing_entry,
                         existing_bowel=existing_bowel)

@bp.route('/add/stress', methods=['GET', 'POST'])
def add_stress():
    """Add or edit stress entry"""
    edit_entry_id = request.args.get('edit', type=int)
    existing_entry = None
    existing_stress = None

    # Load existing entry for editing
    if edit_entry_id:
        existing_entry = DiaryEntry.query.get_or_404(edit_entry_id)
        if existing_entry.entry_type == 'stress' and existing_entry.stress_logs:
            existing_stress = existing_entry.stress_logs[0]

    if request.method == 'POST':
        try:
            # Get form data
            stress_date = datetime.strptime(request.form.get('stress_date'), '%Y-%m-%d').date()
            stress_time = datetime.strptime(request.form.get('stress_time'), '%H:%M').time()

            if edit_entry_id and existing_entry:
                # Update existing entry
                existing_entry.entry_date = stress_date
                existing_entry.entry_time = stress_time

                # Update stress log
                existing_stress.stress_level = int(request.form.get('stress_level'))
                existing_stress.stress_types = ','.join(request.form.getlist('stress_types'))
                existing_stress.physical_symptoms = ','.join(request.form.getlist('physical_symptoms'))
                existing_stress.management_actions = ','.join(request.form.getlist('management_actions'))
                existing_stress.duration_status = request.form.get('duration_status')
                existing_stress.notes = request.form.get('notes', '')

                db.session.commit()
                flash('Stress entry updated successfully!', 'success')
            else:
                # Create new diary entry
                diary_entry = DiaryEntry(
                    entry_date=stress_date,
                    entry_time=stress_time,
                    entry_type='stress'
                )
                db.session.add(diary_entry)
                db.session.flush()

                # Create stress log
                stress = StressLog(
                    diary_entry_id=diary_entry.id,
                    stress_level=int(request.form.get('stress_level')),
                    stress_types=','.join(request.form.getlist('stress_types')),
                    physical_symptoms=','.join(request.form.getlist('physical_symptoms')),
                    management_actions=','.join(request.form.getlist('management_actions')),
                    duration_status=request.form.get('duration_status'),
                    notes=request.form.get('notes', '')
                )
                db.session.add(stress)
                db.session.commit()
                flash('Stress level logged successfully!', 'success')

            return redirect(url_for('diary.day_view', date_string=stress_date.strftime('%Y-%m-%d')))

        except Exception as e:
            db.session.rollback()
            flash(f'Error saving stress: {str(e)}', 'error')
            return redirect(url_for('diary.add_stress'))

    return render_template('diary/entry-stress.html',
                         today=date.today(),
                         existing_entry=existing_entry,
                         existing_stress=existing_stress)

@bp.route('/add/note', methods=['GET', 'POST'])
def add_note():
    """Add or edit general note"""
    edit_entry_id = request.args.get('edit', type=int)
    existing_entry = None
    existing_note = None

    # Load existing entry for editing
    if edit_entry_id:
        existing_entry = DiaryEntry.query.get_or_404(edit_entry_id)
        if existing_entry.entry_type == 'note' and existing_entry.notes:
            existing_note = existing_entry.notes[0]

    if request.method == 'POST':
        try:
            # Get form data
            note_date = datetime.strptime(request.form.get('note_date'), '%Y-%m-%d').date()
            note_time = datetime.strptime(request.form.get('note_time'), '%H:%M').time()

            if edit_entry_id and existing_entry:
                # Update existing entry
                existing_entry.entry_date = note_date
                existing_entry.entry_time = note_time

                # Update note
                existing_note.category = request.form.get('category')
                existing_note.title = request.form.get('title')
                existing_note.content = request.form.get('content')
                existing_note.mood = request.form.get('mood')
                existing_note.tags = request.form.get('tags', '')

                db.session.commit()
                flash('Note updated successfully!', 'success')
            else:
                # Create new diary entry
                diary_entry = DiaryEntry(
                    entry_date=note_date,
                    entry_time=note_time,
                    entry_type='note'
                )
                db.session.add(diary_entry)
                db.session.flush()

                # Create note
                note = Note(
                    diary_entry_id=diary_entry.id,
                    category=request.form.get('category'),
                    title=request.form.get('title'),
                    content=request.form.get('content'),
                    mood=request.form.get('mood'),
                    tags=request.form.get('tags', '')
                )
                db.session.add(note)
                db.session.commit()
                flash('Note added successfully!', 'success')

            return redirect(url_for('diary.day_view', date_string=note_date.strftime('%Y-%m-%d')))

        except Exception as e:
            db.session.rollback()
            flash(f'Error saving note: {str(e)}', 'error')
            return redirect(url_for('diary.add_note'))

    return render_template('diary/entry-note.html',
                         today=date.today(),
                         existing_entry=existing_entry,
                         existing_note=existing_note)

@bp.route('/delete/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    """Delete a diary entry"""
    try:
        entry = DiaryEntry.query.get_or_404(entry_id)
        entry_date = entry.entry_date
        db.session.delete(entry)
        db.session.commit()
        flash('Entry deleted successfully!', 'success')
        return redirect(url_for('diary.day_view', date_string=entry_date.strftime('%Y-%m-%d')))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting entry: {str(e)}', 'error')
        return redirect(url_for('diary.index'))

@bp.route('/trends')
def trends():
    """Symptom trends and analytics view"""
    today = date.today()

    # Get last 30 days of data
    start_date = today - timedelta(days=30)

    # Get all symptom entries in the last 30 days
    symptom_entries = db.session.query(DiaryEntry, Symptom).join(
        Symptom, DiaryEntry.id == Symptom.diary_entry_id
    ).filter(
        DiaryEntry.entry_date >= start_date,
        DiaryEntry.entry_type == 'symptom'
    ).order_by(DiaryEntry.entry_date, DiaryEntry.entry_time).all()

    # Prepare data for charts
    dates = []
    bloating_data = []
    pain_data = []
    wind_data = []
    nausea_data = []
    heartburn_data = []
    headache_data = []
    brain_fog_data = []
    fatigue_data = []
    sinus_data = []

    for entry, symptom in symptom_entries:
        date_str = entry.entry_date.strftime('%Y-%m-%d')
        if date_str not in dates:
            dates.append(date_str)
            bloating_data.append(symptom.bloating)
            pain_data.append(symptom.pain)
            wind_data.append(symptom.wind)
            nausea_data.append(symptom.nausea)
            heartburn_data.append(symptom.heartburn)
            headache_data.append(symptom.headache)
            brain_fog_data.append(symptom.brain_fog)
            fatigue_data.append(symptom.fatigue)
            sinus_data.append(symptom.sinus_issues)
        else:
            # If multiple entries per day, take the max value
            idx = dates.index(date_str)
            bloating_data[idx] = max(bloating_data[idx], symptom.bloating)
            pain_data[idx] = max(pain_data[idx], symptom.pain)
            wind_data[idx] = max(wind_data[idx], symptom.wind)
            nausea_data[idx] = max(nausea_data[idx], symptom.nausea)
            heartburn_data[idx] = max(heartburn_data[idx], symptom.heartburn)
            headache_data[idx] = max(headache_data[idx], symptom.headache)
            brain_fog_data[idx] = max(brain_fog_data[idx], symptom.brain_fog)
            fatigue_data[idx] = max(fatigue_data[idx], symptom.fatigue)
            sinus_data[idx] = max(sinus_data[idx], symptom.sinus_issues)

    # Calculate summary statistics
    total_symptom_days = len(dates)

    avg_bloating = sum(bloating_data) / len(bloating_data) if bloating_data else 0
    avg_pain = sum(pain_data) / len(pain_data) if pain_data else 0
    avg_wind = sum(wind_data) / len(wind_data) if wind_data else 0

    return render_template('diary/trends.html',
                         dates=dates,
                         bloating_data=bloating_data,
                         pain_data=pain_data,
                         wind_data=wind_data,
                         nausea_data=nausea_data,
                         heartburn_data=heartburn_data,
                         headache_data=headache_data,
                         brain_fog_data=brain_fog_data,
                         fatigue_data=fatigue_data,
                         sinus_data=sinus_data,
                         total_symptom_days=total_symptom_days,
                         avg_bloating=round(avg_bloating, 1),
                         avg_pain=round(avg_pain, 1),
                         avg_wind=round(avg_wind, 1))

@bp.route('/weekly')
def weekly_summary():
    """Weekly summary view"""
    today = date.today()

    # Get start of current week (Monday)
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    # Get all entries for the current week
    entries = DiaryEntry.query.filter(
        DiaryEntry.entry_date >= week_start,
        DiaryEntry.entry_date <= week_end
    ).order_by(DiaryEntry.entry_date, DiaryEntry.entry_time).all()

    # Group by day
    days_data = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_entries = [e for e in entries if e.entry_date == day]

        day_data = {
            'date': day,
            'meals': len([e for e in day_entries if e.entry_type == 'meal']),
            'symptoms': len([e for e in day_entries if e.entry_type == 'symptom']),
            'bowel': len([e for e in day_entries if e.entry_type == 'bowel']),
            'stress': len([e for e in day_entries if e.entry_type == 'stress']),
            'total': len(day_entries)
        }
        days_data.append(day_data)

    week_stats = {
        'meals': len([e for e in entries if e.entry_type == 'meal']),
        'symptoms': len([e for e in entries if e.entry_type == 'symptom']),
        'bowel': len([e for e in entries if e.entry_type == 'bowel']),
        'stress': len([e for e in entries if e.entry_type == 'stress']),
        'notes': len([e for e in entries if e.entry_type == 'note']),
        'total': len(entries)
    }

    return render_template('diary/weekly.html',
                         today=today,
                         week_start=week_start,
                         week_end=week_end,
                         days_data=days_data,
                         week_stats=week_stats)
