from database import db
from datetime import datetime

class Food(db.Model):
    """Food database model with FODMAP and histamine information"""
    __tablename__ = 'foods'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    category = db.Column(db.String(100), nullable=False, index=True)

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

    # Additional information
    preparation_notes = db.Column(db.Text)
    common_allergens = db.Column(db.String(200))  # Comma-separated

    # Nutrition Information (for packaged items like beverages)
    # Basic info
    health_star_rating = db.Column(db.Float)  # 0.0 to 5.0
    serving_size = db.Column(db.String(50))  # e.g., "250ml"
    servings_per_pack = db.Column(db.Integer)

    # Energy
    energy_per_serve_kj = db.Column(db.Float)
    energy_per_100_kj = db.Column(db.Float)
    energy_per_serve_cal = db.Column(db.Float)
    energy_per_100_cal = db.Column(db.Float)

    # Macronutrients per serve
    protein_per_serve = db.Column(db.Float)
    fat_per_serve = db.Column(db.Float)
    saturated_fat_per_serve = db.Column(db.Float)
    trans_fat_per_serve = db.Column(db.Float)
    polyunsaturated_fat_per_serve = db.Column(db.Float)
    monounsaturated_fat_per_serve = db.Column(db.Float)
    carbohydrate_per_serve = db.Column(db.Float)
    sugars_per_serve = db.Column(db.Float)
    lactose_per_serve = db.Column(db.Float)
    galactose_per_serve = db.Column(db.Float)
    dietary_fibre_per_serve = db.Column(db.Float)

    # Macronutrients per 100ml/100g
    protein_per_100 = db.Column(db.Float)
    fat_per_100 = db.Column(db.Float)
    saturated_fat_per_100 = db.Column(db.Float)
    trans_fat_per_100 = db.Column(db.Float)
    polyunsaturated_fat_per_100 = db.Column(db.Float)
    monounsaturated_fat_per_100 = db.Column(db.Float)
    carbohydrate_per_100 = db.Column(db.Float)
    sugars_per_100 = db.Column(db.Float)
    lactose_per_100 = db.Column(db.Float)
    galactose_per_100 = db.Column(db.Float)
    dietary_fibre_per_100 = db.Column(db.Float)

    # Cholesterol
    cholesterol_per_serve = db.Column(db.Float)
    cholesterol_per_100 = db.Column(db.Float)

    # Minerals per serve
    sodium_per_serve = db.Column(db.Float)
    potassium_per_serve = db.Column(db.Float)
    calcium_per_serve = db.Column(db.Float)
    phosphorus_per_serve = db.Column(db.Float)

    # Minerals per 100ml/100g
    sodium_per_100 = db.Column(db.Float)
    potassium_per_100 = db.Column(db.Float)
    calcium_per_100 = db.Column(db.Float)
    phosphorus_per_100 = db.Column(db.Float)

    # Vitamins per serve
    vitamin_a_per_serve = db.Column(db.Float)
    vitamin_b12_per_serve = db.Column(db.Float)
    vitamin_d_per_serve = db.Column(db.Float)
    riboflavin_b2_per_serve = db.Column(db.Float)

    # Vitamins per 100ml/100g
    vitamin_a_per_100 = db.Column(db.Float)
    vitamin_b12_per_100 = db.Column(db.Float)
    vitamin_d_per_100 = db.Column(db.Float)
    riboflavin_b2_per_100 = db.Column(db.Float)

    # RDI percentages (optional)
    vitamin_a_rdi_percent = db.Column(db.String(20))
    vitamin_b12_rdi_percent = db.Column(db.String(20))
    vitamin_d_rdi_percent = db.Column(db.String(20))
    riboflavin_b2_rdi_percent = db.Column(db.String(20))
    calcium_rdi_percent = db.Column(db.String(20))
    phosphorus_rdi_percent = db.Column(db.String(20))

    # Ingredients and where to buy
    ingredients_list = db.Column(db.Text)  # Full ingredient list as text
    contains_allergens = db.Column(db.String(200))  # e.g., "gluten"
    may_contain_allergens = db.Column(db.String(200))  # e.g., "Wheat"
    where_to_buy = db.Column(db.Text)  # Store names or links, comma-separated

    # Custom nutrients (stored as JSON)
    # Format: {"vitamins": [{"name": "Vitamin C", "per_serve": 10, "per_100": 4, "unit": "mg", "rdi": "25%", "order": 0}],
    #          "minerals": [...], "macros": [...]}
    custom_nutrients = db.Column(db.Text)  # JSON string for custom vitamins, minerals, macros

    # Units for standard vitamins (when custom unit is needed)
    vitamin_a_unit = db.Column(db.String(20), default='mcg')
    vitamin_b12_unit = db.Column(db.String(20), default='mcg')
    vitamin_d_unit = db.Column(db.String(20), default='mcg')
    riboflavin_b2_unit = db.Column(db.String(20), default='mg')

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Food {self.name}>'

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
