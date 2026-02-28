from database import db
from datetime import datetime


class RecipeClassificationOption(db.Model):
    """Custom classification options for recipes (e.g., cuisines, main ingredients)."""
    __tablename__ = 'recipe_classification_options'

    id = db.Column(db.Integer, primary_key=True)
    option_type = db.Column(db.String(50), nullable=False, index=True)
    value = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('option_type', 'value', name='uq_recipe_classification_option'),
    )

    def __repr__(self):
        return f'<RecipeClassificationOption {self.option_type}: {self.value}>'

    def to_dict(self):
        """Convert classification option to dictionary"""
        return {
            'id': self.id,
            'option_type': self.option_type,
            'value': self.value,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Recipe(db.Model):
    """User-created recipes with ingredients from food library"""
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    servings = db.Column(db.Integer, default=1)
    prep_time = db.Column(db.String(50))  # e.g., "15 minutes"
    cook_time = db.Column(db.String(50))

    instructions = db.Column(db.Text)
    notes = db.Column(db.Text)

    # PRIMARY CATEGORY (Meal Type)
    category = db.Column(db.String(100))  # Breakfast, Lunch, Dinner, Snacks, Desserts, Beverages, Salads, Sauces/Gravies

    # SUBCATEGORIES (stored as tags for searchability)
    subcategory = db.Column(db.String(200))  # e.g., "Green & Chopped Salads", "Protein Salads", etc.

    # ADDITIONAL FILTERS
    cuisine = db.Column(db.String(100))  # Italian, Mexican, Asian, American, Mediterranean, etc.
    dietary_needs = db.Column(db.String(200))  # Keto, Gluten-Free, Dairy-Free, Vegan, Paleo, etc. (comma-separated for multiple)
    preparation_method = db.Column(db.String(200))  # Grilling, BBQ, Baking, Roasting, Slow Cooker, Air Fryer, etc. (comma-separated for multiple)
    occasion = db.Column(db.String(200))  # Thanksgiving, Easter, Game Day, Weeknight Dinners, etc. (comma-separated for multiple)
    difficulty = db.Column(db.String(50))  # Quick & Easy, Under 15 Minutes, Under 30 Minutes, Beginner-Friendly, Intermediate, Advanced

    # LEGACY TAGS (keeping for backward compatibility)
    tags = db.Column(db.String(500))  # Comma-separated custom tags

    # Photo
    image_path = db.Column(db.String(500))  # Path to uploaded recipe photo
    source_url = db.Column(db.String(500))  # Optional source link

    # Relationships
    ingredients = db.relationship('RecipeIngredient', backref='recipe', lazy=True, cascade='all, delete-orphan')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Recipe {self.name}>'

    def get_all_tags(self):
        """Get all tags as a list for display"""
        tags_list = []
        if self.subcategory:
            tags_list.append(self.subcategory)
        if self.cuisine:
            tags_list.append(self.cuisine)
        if self.dietary_needs:
            tags_list.extend([d.strip() for d in self.dietary_needs.split(',') if d.strip()])
        if self.preparation_method:
            tags_list.extend([p.strip() for p in self.preparation_method.split(',') if p.strip()])
        if self.occasion:
            tags_list.extend([o.strip() for o in self.occasion.split(',') if o.strip()])
        if self.difficulty:
            tags_list.append(self.difficulty)
        if self.tags:
            tags_list.extend([t.strip() for t in self.tags.split(',') if t.strip()])
        return tags_list

    def to_dict(self):
        """Convert recipe to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'servings': self.servings,
            'prep_time': self.prep_time,
            'cook_time': self.cook_time,
            'instructions': self.instructions,
            'notes': self.notes,
            'category': self.category,
            'subcategory': self.subcategory,
            'cuisine': self.cuisine,
            'dietary_needs': [d.strip() for d in self.dietary_needs.split(',') if d.strip()] if self.dietary_needs else [],
            'preparation_method': [p.strip() for p in self.preparation_method.split(',') if p.strip()] if self.preparation_method else [],
            'occasion': [o.strip() for o in self.occasion.split(',') if o.strip()] if self.occasion else [],
            'difficulty': self.difficulty,
            'tags': [t.strip() for t in self.tags.split(',') if t.strip()] if self.tags else [],
            'image_path': self.image_path,
            'source_url': self.source_url,
            'ingredients': [ing.to_dict() for ing in self.ingredients],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class RecipeIngredient(db.Model):
    """Junction table for recipes and foods"""
    __tablename__ = 'recipe_ingredients'

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey('foods.id'), nullable=False)

    quantity = db.Column(db.String(100))  # e.g., "100g", "1 cup", "2 pieces"
    notes = db.Column(db.String(200))  # Optional notes like "chopped", "diced"

    # Relationship to food
    food = db.relationship('Food')

    def __repr__(self):
        return f'<RecipeIngredient {self.quantity}>'

    def to_dict(self):
        """Convert recipe ingredient to dictionary"""
        return {
            'id': self.id,
            'recipe_id': self.recipe_id,
            'food_id': self.food_id,
            'food_name': self.food.name if self.food else None,
            'food_category': self.food.category if self.food else None,
            'quantity': self.quantity,
            'notes': self.notes
        }


class SavedMeal(db.Model):
    """Saved custom meal combinations for quick diary entry"""
    __tablename__ = 'saved_meals'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    meal_type = db.Column(db.String(50))  # Breakfast, Lunch, Dinner, Snack

    # Photo
    image_path = db.Column(db.String(500))  # Path to uploaded meal photo

    # Relationships
    meal_items = db.relationship('SavedMealItem', backref='saved_meal', lazy=True, cascade='all, delete-orphan')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SavedMeal {self.name}>'

    def to_dict(self):
        """Convert saved meal to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'meal_type': self.meal_type,
            'image_path': self.image_path,
            'items': [item.to_dict() for item in self.meal_items],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SavedMealItem(db.Model):
    """Junction table for saved meals and foods"""
    __tablename__ = 'saved_meal_items'

    id = db.Column(db.Integer, primary_key=True)
    saved_meal_id = db.Column(db.Integer, db.ForeignKey('saved_meals.id'), nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey('foods.id'), nullable=False)

    portion_size = db.Column(db.String(100))  # e.g., "100g", "1 cup"

    # Relationship to food
    food = db.relationship('Food')

    def __repr__(self):
        return f'<SavedMealItem {self.portion_size}>'

    def to_dict(self):
        """Convert saved meal item to dictionary"""
        return {
            'id': self.id,
            'saved_meal_id': self.saved_meal_id,
            'food_id': self.food_id,
            'food_name': self.food.name if self.food else None,
            'food_category': self.food.category if self.food else None,
            'portion_size': self.portion_size
        }


class ArchivedExternalRecipe(db.Model):
    """Track archived/hidden recipes from external dataset"""
    __tablename__ = 'archived_external_recipes'

    id = db.Column(db.Integer, primary_key=True)
    recipe_hash = db.Column(db.String(32), unique=True, nullable=False, index=True)
    recipe_name = db.Column(db.String(200))  # Store name for reference
    archived_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ArchivedExternalRecipe {self.recipe_name}>'

    def to_dict(self):
        """Convert archived recipe to dictionary"""
        return {
            'id': self.id,
            'recipe_hash': self.recipe_hash,
            'recipe_name': self.recipe_name,
            'archived_at': self.archived_at.isoformat() if self.archived_at else None
        }

    @classmethod
    def get_archived_hashes(cls) -> set:
        """Get set of all archived recipe hashes."""
        return {r.recipe_hash for r in cls.query.all()}

    @classmethod
    def is_archived(cls, recipe_hash: str) -> bool:
        """Check if a recipe hash is archived."""
        return cls.query.filter_by(recipe_hash=recipe_hash).first() is not None

    @classmethod
    def archive_recipe(cls, recipe_hash: str, recipe_name: str = None):
        """Archive a recipe by its hash."""
        if not cls.is_archived(recipe_hash):
            archived = cls(recipe_hash=recipe_hash, recipe_name=recipe_name)
            db.session.add(archived)
            db.session.commit()

    @classmethod
    def unarchive_recipe(cls, recipe_hash: str):
        """Remove a recipe from the archive."""
        archived = cls.query.filter_by(recipe_hash=recipe_hash).first()
        if archived:
            db.session.delete(archived)
            db.session.commit()


class RecipeShare(db.Model):
    """Track shareable recipe links"""
    __tablename__ = 'recipe_shares'

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    share_token = db.Column(db.String(36), unique=True, nullable=False, index=True)  # UUID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    recipe = db.relationship('Recipe', backref='shares')

    def __repr__(self):
        return f'<RecipeShare {self.share_token[:8]}>'

    def to_dict(self):
        """Convert recipe share to dictionary"""
        return {
            'id': self.id,
            'recipe_id': self.recipe_id,
            'recipe_name': self.recipe.name if self.recipe else None,
            'share_token': self.share_token,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
