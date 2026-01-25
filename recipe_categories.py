"""
Recipe Categories and Classification Constants
Based on comprehensive categorization system
"""

# PRIMARY CATEGORIES (Meal Type)
MEAL_TYPES = [
    'Breakfast & Brunch',
    'Lunch & Meal Prep',
    'Dinner',
    'Snacks & Appetizers',
    'Desserts & Baked Goods',
    'Drinks & Smoothies',
    'Salads',
    'Sauces & Gravies'
]

# SUBCATEGORIES for Salads
SALAD_SUBCATEGORIES = [
    'Green & Chopped Salads',
    'Protein Salads (chicken, tuna, shrimp, steak)',
    'Pasta Salads',
    'Grain Salads (quinoa, farro, couscous)',
    'Vegetable-Based Salads',
    'Fruit Salads',
    'Warm Salads',
    'Meal-Prep & Make-Ahead Salads'
]

# SUBCATEGORIES for Sauces & Gravies
SAUCE_SUBCATEGORIES = [
    'Salad Dressings (vinaigrettes, creamy, oil-based)',
    'Sauces & Gravies',
    'Marinades',
    'Dips & Spreads',
    'Condiments (aioli, ketchup, mustard, relish)',
    'Pestos & Herb Sauces',
    'Asian Sauces (soy-based, sesame, chili, teriyaki)',
    'Creamy Sauces',
    'Non-Creamy Sauces',
    'Homemade Sauces',
    'No-Cook Sauces'
]

# Combine all subcategories
ALL_SUBCATEGORIES = SALAD_SUBCATEGORIES + SAUCE_SUBCATEGORIES

# CUISINE / ORIGIN
CUISINES = [
    'Italian',
    'Mexican',
    'Chinese',
    'Japanese',
    'Thai',
    'Korean',
    'Vietnamese',
    'Indian',
    'American',
    'Greek',
    'Turkish',
    'Middle Eastern',
    'French',
    'Spanish',
    'Caribbean',
    'African',
    'Fusion'
]

# MAIN INGREDIENT
MAIN_INGREDIENTS = [
    'Chicken (roasted, grilled, shredded, wings)',
    'Beef (steaks, ground beef, slow-cooked)',
    'Fish & Seafood (salmon, shrimp, shellfish, white fish)',
    'Pork (chops, ribs, tenderloin, bacon)',
    'Vegetarian / Vegan (legumes, tofu, tempeh, vegetables)',
    'Pasta & Grains (rice, quinoa, noodles, couscous)',
    'Eggs & Dairy-Based Dishes'
]

# DIETARY NEEDS / RESTRICTIONS
DIETARY_NEEDS = [
    'Keto & Low-Carb',
    'Gluten-Free',
    'Dairy-Free',
    'Vegan & Plant-Based',
    'Paleo & Whole30',
    'Heart-Healthy or Low-Fat',
    'Nut-Free',
    'Soy-Free',
    'Egg-Free'
]

# PREPARATION METHOD
PREPARATION_METHODS = [
    'Grilling & BBQ',
    'Baking & Roasting',
    'Slow Cooker / Crockpot',
    'Air Fryer',
    'Stovetop / Skillet Meals',
    'No-Cook or Minimal-Prep',
    'One-Pot or Sheet-Pan Meals'
]

# OCCASION / HOLIDAY
OCCASIONS = [
    'Thanksgiving & Christmas',
    'Easter & Holiday Brunch',
    'Halloween & Themed Parties',
    'Game Day & Tailgating',
    'Potlucks & Family Gatherings',
    'Weeknight Dinners',
    'Romantic or Special-Occasion Meals'
]

# PREPARATION TIME / DIFFICULTY
DIFFICULTY_LEVELS = [
    'Quick & Easy',
    'Under 15 Minutes',
    'Under 30 Minutes',
    'Make-Ahead Meals',
    'Beginner-Friendly',
    'Intermediate',
    'Advanced / Gourmet Recipes'
]

def get_subcategories_for_category(category):
    """Get appropriate subcategories based on primary category"""
    if category == 'Salads':
        return SALAD_SUBCATEGORIES
    elif category == 'Sauces & Gravies':
        return SAUCE_SUBCATEGORIES
    else:
        return []
