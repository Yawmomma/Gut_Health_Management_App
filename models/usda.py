"""USDA FoodData Central database models"""
from database import db
from datetime import datetime


class USDAFoodCategory(db.Model):
    """USDA food category (e.g., 'Dairy and Egg Products', 'Fruits and Fruit Juices')"""
    __tablename__ = 'usda_food_categories'

    id = db.Column(db.Integer, primary_key=True)
    usda_category_id = db.Column(db.Integer, unique=True, index=True)
    description = db.Column(db.String(200), nullable=False)
    food_count = db.Column(db.Integer, default=0)

    # Relationship to foods
    foods = db.relationship('USDAFood', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<USDAFoodCategory {self.description}>'


class USDAFood(db.Model):
    """USDA food item from FoodData Central"""
    __tablename__ = 'usda_foods'

    id = db.Column(db.Integer, primary_key=True)
    fdc_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    description = db.Column(db.String(500), nullable=False, index=True)
    data_type = db.Column(db.String(50))  # "Foundation" or "SR Legacy"
    category_id = db.Column(db.Integer, db.ForeignKey('usda_food_categories.id'))

    # Additional metadata
    scientific_name = db.Column(db.String(200))
    common_names = db.Column(db.Text)  # Comma-separated
    food_class = db.Column(db.String(50))  # e.g., "FinalFood"
    publication_date = db.Column(db.String(20))

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    nutrients = db.relationship('USDAFoodNutrient', backref='food', lazy='dynamic', cascade='all, delete-orphan')
    portions = db.relationship('USDAFoodPortion', backref='food', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<USDAFood {self.fdc_id}: {self.description[:50]}>'

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'fdc_id': self.fdc_id,
            'description': self.description,
            'data_type': self.data_type,
            'category': self.category.description if self.category else None,
            'scientific_name': self.scientific_name,
            'common_names': self.common_names
        }

    def get_nutrient_value(self, nutrient_name):
        """Get nutrient value by name"""
        for fn in self.nutrients:
            if fn.nutrient and fn.nutrient.name.lower() == nutrient_name.lower():
                return fn.amount
        return None

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
        # Sort nutrients within each group by name
        for group in groups:
            groups[group].sort(key=lambda x: x['name'])
        return groups


class USDANutrient(db.Model):
    """Nutrient definition (e.g., Protein, Vitamin A)"""
    __tablename__ = 'usda_nutrients'

    id = db.Column(db.Integer, primary_key=True)
    nutrient_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    unit_name = db.Column(db.String(20))  # g, mg, mcg, kcal, kJ, IU
    nutrient_group = db.Column(db.String(100))  # Proximates, Vitamins, Minerals, Lipids, etc.
    rank = db.Column(db.Integer)  # Display order

    def __repr__(self):
        return f'<USDANutrient {self.name} ({self.unit_name})>'


class USDAFoodNutrient(db.Model):
    """Nutrient value for a specific food (junction table)"""
    __tablename__ = 'usda_food_nutrients'

    id = db.Column(db.Integer, primary_key=True)
    food_id = db.Column(db.Integer, db.ForeignKey('usda_foods.id', ondelete='CASCADE'), nullable=False, index=True)
    nutrient_id = db.Column(db.Integer, db.ForeignKey('usda_nutrients.id'), nullable=False, index=True)
    amount = db.Column(db.Float)  # Amount per 100g

    # Relationship to nutrient definition
    nutrient = db.relationship('USDANutrient')

    # Unique constraint to prevent duplicates
    __table_args__ = (
        db.UniqueConstraint('food_id', 'nutrient_id', name='uq_food_nutrient'),
    )

    def __repr__(self):
        return f'<USDAFoodNutrient food={self.food_id} nutrient={self.nutrient_id} amount={self.amount}>'


class USDAFoodPortion(db.Model):
    """Serving size/portion for a food"""
    __tablename__ = 'usda_food_portions'

    id = db.Column(db.Integer, primary_key=True)
    food_id = db.Column(db.Integer, db.ForeignKey('usda_foods.id', ondelete='CASCADE'), nullable=False, index=True)
    usda_portion_id = db.Column(db.Integer)  # USDA's portion ID
    portion_description = db.Column(db.String(200))  # e.g., "1 cup, sliced"
    gram_weight = db.Column(db.Float)  # Weight in grams
    amount = db.Column(db.Float)  # e.g., 1.0
    modifier = db.Column(db.String(100))  # e.g., "sliced", "chopped"
    measure_unit = db.Column(db.String(50))  # e.g., "cup", "tbsp"
    sequence_number = db.Column(db.Integer)  # Display order

    def __repr__(self):
        return f'<USDAFoodPortion {self.portion_description} ({self.gram_weight}g)>'

    def get_display_text(self):
        """Get formatted display text for the portion"""
        if self.portion_description:
            return self.portion_description
        parts = []
        if self.amount:
            parts.append(str(self.amount))
        if self.measure_unit:
            parts.append(self.measure_unit)
        if self.modifier:
            parts.append(f"({self.modifier})")
        return ' '.join(parts) if parts else 'Standard portion'
