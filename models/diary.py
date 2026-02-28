from database import db
from datetime import datetime

class DiaryEntry(db.Model):
    """Main diary entry - parent for all daily logs"""
    __tablename__ = 'diary_entries'

    id = db.Column(db.Integer, primary_key=True)
    entry_date = db.Column(db.Date, nullable=False, index=True)
    entry_time = db.Column(db.Time, nullable=False)
    entry_type = db.Column(db.String(50), nullable=False)  # meal, symptom, bowel, stress, note

    # Relationships
    meals = db.relationship('Meal', backref='diary_entry', lazy=True, cascade='all, delete-orphan')
    symptoms = db.relationship('Symptom', backref='diary_entry', lazy=True, cascade='all, delete-orphan')
    bowel_movements = db.relationship('BowelMovement', backref='diary_entry', lazy=True, cascade='all, delete-orphan')
    stress_logs = db.relationship('StressLog', backref='diary_entry', lazy=True, cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='diary_entry', lazy=True, cascade='all, delete-orphan')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<DiaryEntry {self.entry_date} {self.entry_time} - {self.entry_type}>'

    def to_dict(self):
        """Convert diary entry to dictionary"""
        return {
            'id': self.id,
            'entry_date': self.entry_date.isoformat() if self.entry_date else None,
            'entry_time': self.entry_time.isoformat() if self.entry_time else None,
            'entry_type': self.entry_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'meals': [meal.to_dict() for meal in self.meals] if self.entry_type == 'meal' else [],
            'symptoms': [symptom.to_dict() for symptom in self.symptoms] if self.entry_type == 'symptom' else [],
            'bowel_movements': [bm.to_dict() for bm in self.bowel_movements] if self.entry_type == 'bowel' else [],
            'stress_logs': [stress.to_dict() for stress in self.stress_logs] if self.entry_type == 'stress' else [],
            'notes': [note.to_dict() for note in self.notes] if self.entry_type == 'note' else []
        }


class Meal(db.Model):
    """Meal entry with foods consumed"""
    __tablename__ = 'meals'

    id = db.Column(db.Integer, primary_key=True)
    diary_entry_id = db.Column(db.Integer, db.ForeignKey('diary_entries.id'), nullable=False)

    meal_type = db.Column(db.String(50))  # Breakfast, Lunch, Dinner, Snack
    location = db.Column(db.String(100))  # Home, Restaurant, Work, Travel
    preparation = db.Column(db.String(50))  # Fresh, Leftover, Reheated, Restaurant

    # Optional reference to recipe if meal was created from a recipe
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=True)

    notes = db.Column(db.Text)

    # Relationships
    meal_foods = db.relationship('MealFood', backref='meal', lazy=True, cascade='all, delete-orphan')
    recipe = db.relationship('Recipe', foreign_keys=[recipe_id])

    def __repr__(self):
        return f'<Meal {self.meal_type}>'

    def to_dict(self):
        """Convert meal to dictionary"""
        return {
            'id': self.id,
            'diary_entry_id': self.diary_entry_id,
            'meal_type': self.meal_type,
            'location': self.location,
            'preparation': self.preparation,
            'recipe_id': self.recipe_id,
            'notes': self.notes,
            'foods': [mf.to_dict() for mf in self.meal_foods]
        }


class MealFood(db.Model):
    """Junction table for meals and foods with portion sizes"""
    __tablename__ = 'meal_foods'

    id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meals.id'), nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey('foods.id'), nullable=False)

    portion_size = db.Column(db.String(100))  # e.g., "100g", "1 cup"
    serving_type = db.Column(db.String(20))  # 'safe', 'moderate', or 'high'

    # Calculated nutrition values (based on portion size)
    num_servings = db.Column(db.Float)  # Number of servings consumed
    energy_kj = db.Column(db.Float)  # Calculated energy in kJ
    protein_g = db.Column(db.Float)  # Calculated protein in grams
    fat_g = db.Column(db.Float)  # Calculated fat in grams
    carbs_g = db.Column(db.Float)  # Calculated carbohydrates in grams
    sodium_mg = db.Column(db.Float)  # Calculated sodium in mg

    # Relationship to food
    food = db.relationship('Food')

    def to_dict(self):
        """Convert meal food to dictionary"""
        return {
            'id': self.id,
            'meal_id': self.meal_id,
            'food_id': self.food_id,
            'food_name': self.food.name if self.food else None,
            'food_category': self.food.category if self.food else None,
            'portion_size': self.portion_size,
            'serving_type': self.serving_type,
            'num_servings': self.num_servings,
            'energy_kj': self.energy_kj,
            'protein_g': self.protein_g,
            'fat_g': self.fat_g,
            'carbs_g': self.carbs_g,
            'sodium_mg': self.sodium_mg
        }


class Symptom(db.Model):
    """Symptom tracking"""
    __tablename__ = 'symptoms'

    id = db.Column(db.Integer, primary_key=True)
    diary_entry_id = db.Column(db.Integer, db.ForeignKey('diary_entries.id'), nullable=False)

    # Main symptoms (0-10 scale)
    bloating = db.Column(db.Integer, default=0)
    pain = db.Column(db.Integer, default=0)
    wind = db.Column(db.Integer, default=0)

    # Additional symptoms
    nausea = db.Column(db.Integer, default=0)
    heartburn = db.Column(db.Integer, default=0)
    headache = db.Column(db.Integer, default=0)
    brain_fog = db.Column(db.Integer, default=0)
    fatigue = db.Column(db.Integer, default=0)
    sinus_issues = db.Column(db.Integer, default=0)

    severity = db.Column(db.String(20))  # Mild, Moderate, Severe, Extreme
    duration = db.Column(db.String(50))  # <30min, 30-60min, etc.

    notes = db.Column(db.Text)

    def __repr__(self):
        return f'<Symptom severity={self.severity}>'

    def to_dict(self):
        """Convert symptom to dictionary"""
        return {
            'id': self.id,
            'diary_entry_id': self.diary_entry_id,
            'bloating': self.bloating,
            'pain': self.pain,
            'wind': self.wind,
            'nausea': self.nausea,
            'heartburn': self.heartburn,
            'headache': self.headache,
            'brain_fog': self.brain_fog,
            'fatigue': self.fatigue,
            'sinus_issues': self.sinus_issues,
            'severity': self.severity,
            'duration': self.duration,
            'notes': self.notes
        }


class BowelMovement(db.Model):
    """Bowel movement tracking with Bristol Stool Chart"""
    __tablename__ = 'bowel_movements'

    id = db.Column(db.Integer, primary_key=True)
    diary_entry_id = db.Column(db.Integer, db.ForeignKey('diary_entries.id'), nullable=False)

    bristol_type = db.Column(db.Integer, nullable=False)  # 1-7

    urgency = db.Column(db.String(20))  # Normal, Urgent, Very Urgent
    completeness = db.Column(db.String(20))  # Complete, Incomplete
    straining = db.Column(db.String(20))  # None, Mild, Severe

    blood_present = db.Column(db.Boolean, default=False)
    mucus_present = db.Column(db.Boolean, default=False)
    color = db.Column(db.String(50))  # Normal, Pale, Dark, Other

    notes = db.Column(db.Text)

    def __repr__(self):
        return f'<BowelMovement Type {self.bristol_type}>'

    def to_dict(self):
        """Convert bowel movement to dictionary"""
        return {
            'id': self.id,
            'diary_entry_id': self.diary_entry_id,
            'bristol_type': self.bristol_type,
            'urgency': self.urgency,
            'completeness': self.completeness,
            'straining': self.straining,
            'blood_present': self.blood_present,
            'mucus_present': self.mucus_present,
            'color': self.color,
            'notes': self.notes
        }


class StressLog(db.Model):
    """Stress level tracking"""
    __tablename__ = 'stress_logs'

    id = db.Column(db.Integer, primary_key=True)
    diary_entry_id = db.Column(db.Integer, db.ForeignKey('diary_entries.id'), nullable=False)

    stress_level = db.Column(db.Integer, nullable=False)  # 0-10 scale

    # Stress types (stored as comma-separated)
    stress_types = db.Column(db.String(500))

    # Physical symptoms (stored as comma-separated)
    physical_symptoms = db.Column(db.String(500))

    # Management actions taken (stored as comma-separated)
    management_actions = db.Column(db.String(500))

    duration_status = db.Column(db.String(50))  # Ongoing, Acute, Resolved

    notes = db.Column(db.Text)

    def __repr__(self):
        return f'<StressLog level={self.stress_level}>'

    def to_dict(self):
        """Convert stress log to dictionary"""
        return {
            'id': self.id,
            'diary_entry_id': self.diary_entry_id,
            'stress_level': self.stress_level,
            'stress_types': [t.strip() for t in self.stress_types.split(',') if t.strip()] if self.stress_types else [],
            'physical_symptoms': [s.strip() for s in self.physical_symptoms.split(',') if s.strip()] if self.physical_symptoms else [],
            'management_actions': [a.strip() for a in self.management_actions.split(',') if a.strip()] if self.management_actions else [],
            'duration_status': self.duration_status,
            'notes': self.notes
        }


class Note(db.Model):
    """General notes and observations"""
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    diary_entry_id = db.Column(db.Integer, db.ForeignKey('diary_entries.id'), nullable=False)

    category = db.Column(db.String(100))  # General, Treatment, Exercise, etc.
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)

    mood = db.Column(db.String(50))  # Emoji or text representation
    tags = db.Column(db.String(500))  # Comma-separated tags

    def __repr__(self):
        return f'<Note {self.title}>'

    def to_dict(self):
        """Convert note to dictionary"""
        return {
            'id': self.id,
            'diary_entry_id': self.diary_entry_id,
            'category': self.category,
            'title': self.title,
            'content': self.content,
            'mood': self.mood,
            'tags': [t.strip() for t in self.tags.split(',') if t.strip()] if self.tags else []
        }


class MealPlan(db.Model):
    """Represents a saved meal plan (e.g., 7-day plan)"""
    __tablename__ = 'meal_plans'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    days = db.relationship('MealPlanDay', backref='plan', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f'<MealPlan {self.name}>'

    def to_dict(self):
        """Convert meal plan to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'notes': self.notes,
            'days_count': self.days.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class MealPlanDay(db.Model):
    """Represents a day in a meal plan"""
    __tablename__ = 'meal_plan_days'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('meal_plans.id'), nullable=False)
    plan_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    meals = db.relationship('MealPlanItem', backref='day', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f'<MealPlanDay {self.plan_date}>'

    def to_dict(self):
        """Convert meal plan day to dictionary"""
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'plan_date': self.plan_date.isoformat() if self.plan_date else None,
            'meals_count': self.meals.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class MealPlanItem(db.Model):
    """Represents a meal in a meal plan day"""
    __tablename__ = 'meal_plan_items'

    id = db.Column(db.Integer, primary_key=True)
    day_id = db.Column(db.Integer, db.ForeignKey('meal_plan_days.id'), nullable=False)
    meal_type = db.Column(db.String(50))  # Breakfast, Lunch, Dinner, Snack
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=True)
    saved_meal_id = db.Column(db.Integer, db.ForeignKey('saved_meals.id'), nullable=True)
    food_id = db.Column(db.Integer, db.ForeignKey('foods.id'), nullable=True)
    custom_label = db.Column(db.String(200))  # Free-text if no linked entity
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    recipe = db.relationship('Recipe', backref='meal_plan_items')
    saved_meal = db.relationship('SavedMeal', backref='meal_plan_items')
    food = db.relationship('Food', backref='meal_plan_items')

    def __repr__(self):
        return f'<MealPlanItem {self.meal_type}>'

    def to_dict(self):
        """Convert meal plan item to dictionary"""
        return {
            'id': self.id,
            'day_id': self.day_id,
            'meal_type': self.meal_type,
            'recipe_id': self.recipe_id,
            'recipe_name': self.recipe.name if self.recipe else None,
            'saved_meal_id': self.saved_meal_id,
            'saved_meal_name': self.saved_meal.name if self.saved_meal else None,
            'food_id': self.food_id,
            'food_name': self.food.name if self.food else None,
            'custom_label': self.custom_label,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
