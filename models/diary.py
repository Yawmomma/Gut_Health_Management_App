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
