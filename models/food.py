from database import db
from datetime import datetime

class Food(db.Model):
    """Food database model with FODMAP and histamine information"""
    __tablename__ = 'foods'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    category = db.Column(db.String(100), nullable=False, index=True)

    # Link to USDA database for nutritional information
    usda_food_id = db.Column(db.Integer, db.ForeignKey('usda_foods.id'), nullable=True, index=True)

    # Link to AUSNUT 2023 database for Australian nutritional information
    ausnut_food_id = db.Column(db.Integer, db.ForeignKey('ausnut_foods.id'), nullable=True, index=True)

    # FODMAP content (green/amber/red or Low/Medium/High) - Legacy single rating
    fructans = db.Column(db.String(20))
    gos = db.Column(db.String(20))
    lactose = db.Column(db.String(20))
    fructose = db.Column(db.String(20))
    polyols = db.Column(db.String(20))
    mannitol = db.Column(db.String(20))
    sorbitol = db.Column(db.String(20))

    # Safe serving FODMAP ratings
    safe_fructans = db.Column(db.String(20))
    safe_gos = db.Column(db.String(20))
    safe_lactose = db.Column(db.String(20))
    safe_fructose = db.Column(db.String(20))
    safe_polyols = db.Column(db.String(20))
    safe_mannitol = db.Column(db.String(20))
    safe_sorbitol = db.Column(db.String(20))

    # Moderate serving FODMAP ratings
    moderate_fructans = db.Column(db.String(20))
    moderate_gos = db.Column(db.String(20))
    moderate_lactose = db.Column(db.String(20))
    moderate_fructose = db.Column(db.String(20))
    moderate_polyols = db.Column(db.String(20))
    moderate_mannitol = db.Column(db.String(20))
    moderate_sorbitol = db.Column(db.String(20))

    # High serving FODMAP ratings
    high_fructans = db.Column(db.String(20))
    high_gos = db.Column(db.String(20))
    high_lactose = db.Column(db.String(20))
    high_fructose = db.Column(db.String(20))
    high_polyols = db.Column(db.String(20))
    high_mannitol = db.Column(db.String(20))
    high_sorbitol = db.Column(db.String(20))

    # Histamine information - Legacy single rating
    histamine_level = db.Column(db.String(50))  # Low/Medium/High
    histamine_liberator = db.Column(db.String(10))  # Yes/No
    dao_blocker = db.Column(db.String(10))  # Yes/No

    # Safe serving histamine ratings
    safe_histamine_level = db.Column(db.String(50))
    safe_histamine_liberator = db.Column(db.String(10))
    safe_dao_blocker = db.Column(db.String(10))

    # Moderate serving histamine ratings
    moderate_histamine_level = db.Column(db.String(50))
    moderate_histamine_liberator = db.Column(db.String(10))
    moderate_dao_blocker = db.Column(db.String(10))

    # High serving histamine ratings
    high_histamine_level = db.Column(db.String(50))
    high_histamine_liberator = db.Column(db.String(10))
    high_dao_blocker = db.Column(db.String(10))

    # Serving sizes
    safe_serving = db.Column(db.String(100))
    safe_serving_unit = db.Column(db.String(20))
    moderate_serving = db.Column(db.String(100))
    moderate_serving_unit = db.Column(db.String(20))
    high_serving = db.Column(db.String(100))
    high_serving_unit = db.Column(db.String(20))

    # Serving types and notes
    safe_serving_type = db.Column(db.String(50))
    safe_serving_note = db.Column(db.String(200))
    moderate_serving_type = db.Column(db.String(50))
    moderate_serving_note = db.Column(db.String(200))
    high_serving_type = db.Column(db.String(50))
    high_serving_note = db.Column(db.String(200))

    # Traffic light colors for each serving type
    safe_traffic_light = db.Column(db.String(20), default='Green')
    moderate_traffic_light = db.Column(db.String(20), default='Amber')
    high_traffic_light = db.Column(db.String(20), default='Red')

    # Additional information
    preparation_notes = db.Column(db.Text)
    common_allergens = db.Column(db.String(200))  # Comma-separated

    # Custom nutrients (stored as JSON for user-entered nutritional data when USDA link unavailable)
    custom_nutrients = db.Column(db.Text)  # JSON string

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_complete = db.Column(db.Boolean, default=True)  # False for quick-added foods needing more info

    # Relationship to USDA food (for accessing nutritional data)
    usda_food = db.relationship('USDAFood', foreign_keys=[usda_food_id], backref='fodmap_foods', lazy='joined')
    ausnut_food = db.relationship('AUSNUTFood', foreign_keys=[ausnut_food_id], backref='fodmap_foods', lazy='joined')

    def __repr__(self):
        return f'<Food {self.name}>'

    # Backward compatibility properties for removed nutrient fields
    # All return None since we now use USDA data via usda_food relationship
    @property
    def health_star_rating(self):
        return None

    @property
    def serving_size(self):
        return None

    @property
    def servings_per_pack(self):
        return None

    @property
    def energy_per_serve_kj(self):
        return None

    @property
    def energy_per_100_kj(self):
        return None

    @property
    def energy_per_serve_cal(self):
        return None

    @property
    def energy_per_100_cal(self):
        return None

    @property
    def protein_per_serve(self):
        return None

    @property
    def protein_per_100(self):
        return None

    @property
    def fat_per_serve(self):
        return None

    @property
    def fat_per_100(self):
        return None

    @property
    def carbohydrate_per_serve(self):
        return None

    @property
    def carbohydrate_per_100(self):
        return None

    @property
    def sugars_per_serve(self):
        return None

    @property
    def sugars_per_100(self):
        return None

    @property
    def dietary_fibre_per_serve(self):
        return None

    @property
    def dietary_fibre_per_100(self):
        return None

    @property
    def sodium_per_serve(self):
        return None

    @property
    def sodium_per_100(self):
        return None

    @property
    def ingredients_list(self):
        return None

    @property
    def contains_allergens(self):
        return None

    @property
    def may_contain_allergens(self):
        return None

    @property
    def where_to_buy(self):
        return None

    @property
    def saturated_fat_per_serve(self):
        return None

    @property
    def saturated_fat_per_100(self):
        return None

    @property
    def trans_fat_per_serve(self):
        return None

    @property
    def trans_fat_per_100(self):
        return None

    @property
    def polyunsaturated_fat_per_serve(self):
        return None

    @property
    def polyunsaturated_fat_per_100(self):
        return None

    @property
    def monounsaturated_fat_per_serve(self):
        return None

    @property
    def monounsaturated_fat_per_100(self):
        return None

    @property
    def lactose_per_serve(self):
        return None

    @property
    def lactose_per_100(self):
        return None

    @property
    def galactose_per_serve(self):
        return None

    @property
    def galactose_per_100(self):
        return None

    @property
    def cholesterol_per_serve(self):
        return None

    @property
    def cholesterol_per_100(self):
        return None

    @property
    def potassium_per_serve(self):
        return None

    @property
    def potassium_per_100(self):
        return None

    @property
    def calcium_per_serve(self):
        return None

    @property
    def calcium_per_100(self):
        return None

    @property
    def phosphorus_per_serve(self):
        return None

    @property
    def phosphorus_per_100(self):
        return None

    @property
    def vitamin_a_per_serve(self):
        return None

    @property
    def vitamin_a_per_100(self):
        return None

    @property
    def vitamin_a_unit(self):
        return None

    @property
    def vitamin_b12_per_serve(self):
        return None

    @property
    def vitamin_b12_per_100(self):
        return None

    @property
    def vitamin_b12_unit(self):
        return None

    @property
    def vitamin_d_per_serve(self):
        return None

    @property
    def vitamin_d_per_100(self):
        return None

    @property
    def vitamin_d_unit(self):
        return None

    @property
    def riboflavin_b2_per_serve(self):
        return None

    @property
    def riboflavin_b2_per_100(self):
        return None

    @property
    def riboflavin_b2_unit(self):
        return None

    def to_recipe_dict(self):
        """Convert food to lightweight dictionary for recipe/meal forms."""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'fructans': self.fructans,
            'gos': self.gos,
            'lactose': self.lactose,
            'fructose': self.fructose,
            'polyols': self.polyols,
            'mannitol': self.mannitol,
            'sorbitol': self.sorbitol,
            'histamine_level': self.histamine_level,
            'safe_serving': self.safe_serving
        }

    def to_dict(self):
        """Convert food to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            # Legacy single ratings
            'fodmap': {
                'fructans': self.fructans,
                'gos': self.gos,
                'lactose': self.lactose,
                'fructose': self.fructose,
                'polyols': self.polyols,
                'mannitol': self.mannitol,
                'sorbitol': self.sorbitol
            },
            'histamine': {
                'level': self.histamine_level,
                'liberator': self.histamine_liberator,
                'dao_blocker': self.dao_blocker
            },
            # Serving sizes
            'servings': {
                'safe': {
                    'size': self.safe_serving,
                    'type': self.safe_serving_type,
                    'note': self.safe_serving_note,
                    'fodmap': {
                        'fructans': self.safe_fructans,
                        'gos': self.safe_gos,
                        'lactose': self.safe_lactose,
                        'fructose': self.safe_fructose,
                        'polyols': self.safe_polyols,
                        'mannitol': self.safe_mannitol,
                        'sorbitol': self.safe_sorbitol
                    },
                    'histamine': {
                        'level': self.safe_histamine_level,
                        'liberator': self.safe_histamine_liberator,
                        'dao_blocker': self.safe_dao_blocker
                    }
                },
                'moderate': {
                    'size': self.moderate_serving,
                    'type': self.moderate_serving_type,
                    'note': self.moderate_serving_note,
                    'fodmap': {
                        'fructans': self.moderate_fructans,
                        'gos': self.moderate_gos,
                        'lactose': self.moderate_lactose,
                        'fructose': self.moderate_fructose,
                        'polyols': self.moderate_polyols,
                        'mannitol': self.moderate_mannitol,
                        'sorbitol': self.moderate_sorbitol
                    },
                    'histamine': {
                        'level': self.moderate_histamine_level,
                        'liberator': self.moderate_histamine_liberator,
                        'dao_blocker': self.moderate_dao_blocker
                    }
                },
                'high': {
                    'size': self.high_serving,
                    'type': self.high_serving_type,
                    'note': self.high_serving_note,
                    'fodmap': {
                        'fructans': self.high_fructans,
                        'gos': self.high_gos,
                        'lactose': self.high_lactose,
                        'fructose': self.high_fructose,
                        'polyols': self.high_polyols,
                        'mannitol': self.high_mannitol,
                        'sorbitol': self.high_sorbitol
                    },
                    'histamine': {
                        'level': self.high_histamine_level,
                        'liberator': self.high_histamine_liberator,
                        'dao_blocker': self.high_dao_blocker
                    }
                }
            },
            'preparation_notes': self.preparation_notes,
            'common_allergens': self.common_allergens
        }
