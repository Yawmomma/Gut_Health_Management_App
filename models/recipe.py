from database import db
from datetime import datetime

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
    category = db.Column(db.String(100))  # Breakfast & Brunch, Lunch & Meal Prep, Dinner, Snacks & Appetizers, Desserts & Baked Goods, Drinks & Smoothies, Salads, Sauces & Gravies

    # SUBCATEGORIES (stored as tags for searchability)
    subcategory = db.Column(db.String(200))  # e.g., "Green & Chopped Salads", "Protein Salads", etc.

    # ADDITIONAL FILTERS
    cuisine = db.Column(db.String(100))  # Italian, Mexican, Asian, American, Mediterranean, etc.
    main_ingredient = db.Column(db.String(100))  # Chicken, Beef, Fish & Seafood, Pork, Vegetarian/Vegan, etc.
    dietary_needs = db.Column(db.String(200))  # Keto, Gluten-Free, Dairy-Free, Vegan, Paleo, etc. (comma-separated for multiple)
    preparation_method = db.Column(db.String(100))  # Grilling & BBQ, Baking & Roasting, Slow Cooker, Air Fryer, etc.
    occasion = db.Column(db.String(100))  # Thanksgiving, Easter, Game Day, Weeknight Dinners, etc.
    difficulty = db.Column(db.String(50))  # Quick & Easy, Under 15 Minutes, Under 30 Minutes, Beginner-Friendly, Intermediate, Advanced

    # LEGACY TAGS (keeping for backward compatibility)
    tags = db.Column(db.String(500))  # Comma-separated custom tags

    # Photo
    image_path = db.Column(db.String(500))  # Path to uploaded recipe photo

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
        if self.main_ingredient:
            tags_list.append(self.main_ingredient)
        if self.dietary_needs:
            tags_list.extend([d.strip() for d in self.dietary_needs.split(',') if d.strip()])
        if self.preparation_method:
            tags_list.append(self.preparation_method)
        if self.occasion:
            tags_list.append(self.occasion)
        if self.difficulty:
            tags_list.append(self.difficulty)
        if self.tags:
            tags_list.extend([t.strip() for t in self.tags.split(',') if t.strip()])
        return tags_list


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
