"""AUSNUT 2023 Australian food database models"""
from database import db
from datetime import datetime


class AUSNUTFood(db.Model):
    """AUSNUT 2023 food item"""
    __tablename__ = 'ausnut_foods'

    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    public_food_key = db.Column(db.String(20), index=True)
    derivation = db.Column(db.String(50))
    food_name = db.Column(db.String(500), nullable=False, index=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    nutrients = db.relationship('AUSNUTFoodNutrient', backref='food', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<AUSNUTFood {self.survey_id}: {self.food_name[:50]}>'

    def to_dict(self):
        return {
            'id': self.id,
            'survey_id': self.survey_id,
            'public_food_key': self.public_food_key,
            'food_name': self.food_name,
            'derivation': self.derivation,
        }

    def get_nutrients_by_group(self):
        """Get nutrients organized by group"""
        groups = {}
        for fn in self.nutrients:
            if fn.nutrient and fn.amount is not None:
                group = fn.nutrient.nutrient_group or 'Other'
                if group not in groups:
                    groups[group] = []
                groups[group].append({
                    'name': fn.nutrient.name,
                    'amount': fn.amount,
                    'unit': fn.nutrient.unit_name
                })
        for group in groups:
            groups[group].sort(key=lambda x: x['name'])
        return groups


class AUSNUTNutrient(db.Model):
    """AUSNUT nutrient definition"""
    __tablename__ = 'ausnut_nutrients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    unit_name = db.Column(db.String(20))
    nutrient_group = db.Column(db.String(100))
    rank = db.Column(db.Integer)

    def __repr__(self):
        return f'<AUSNUTNutrient {self.name} ({self.unit_name})>'


class AUSNUTFoodNutrient(db.Model):
    """Nutrient value for a specific AUSNUT food"""
    __tablename__ = 'ausnut_food_nutrients'

    id = db.Column(db.Integer, primary_key=True)
    food_id = db.Column(db.Integer, db.ForeignKey('ausnut_foods.id', ondelete='CASCADE'), nullable=False, index=True)
    nutrient_id = db.Column(db.Integer, db.ForeignKey('ausnut_nutrients.id'), nullable=False, index=True)
    amount = db.Column(db.Float)

    nutrient = db.relationship('AUSNUTNutrient')

    __table_args__ = (
        db.UniqueConstraint('food_id', 'nutrient_id', name='uq_ausnut_food_nutrient'),
    )

    def __repr__(self):
        return f'<AUSNUTFoodNutrient food={self.food_id} nutrient={self.nutrient_id} amount={self.amount}>'
