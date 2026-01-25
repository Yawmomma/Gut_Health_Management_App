"""
Seed script to populate the food database with FODMAP and histamine data
Run this script to add sample foods to your database
"""

import sys
import os
# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db
from models.food import Food
from app import app

# Sample foods with FODMAP and Histamine data
SAMPLE_FOODS = [
    # FRUITS
    {
        'name': 'Banana (ripe)',
        'category': 'Fruits',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Low',
        'histamine_liberator': False,
        'dao_blocker': False,
        'safe_serving': '1 medium (100g)',
        'moderate_serving': '2 medium',
        'high_serving': '3+ medium',
        'preparation_notes': 'Choose firm, not overripe bananas for lower histamine. Freeze before overripe.',
        'common_allergens': ''
    },
    {
        'name': 'Strawberries',
        'category': 'Fruits',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Amber',
        'polyols': 'Green',
        'histamine_level': 'Moderate',
        'histamine_liberator': True,
        'dao_blocker': False,
        'safe_serving': '5 medium (65g)',
        'moderate_serving': '10 medium',
        'high_serving': '15+ medium',
        'preparation_notes': 'Very fresh only. Histamine increases as they age. Avoid if overripe.',
        'common_allergens': ''
    },
    {
        'name': 'Blueberries',
        'category': 'Fruits',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Low',
        'histamine_liberator': False,
        'dao_blocker': False,
        'safe_serving': '1/4 cup (40g)',
        'moderate_serving': '1/2 cup',
        'high_serving': '1+ cup',
        'preparation_notes': 'Fresh or frozen both safe. Great for gut health.',
        'common_allergens': ''
    },
    {
        'name': 'Orange',
        'category': 'Fruits',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Amber',
        'polyols': 'Green',
        'histamine_level': 'High',
        'histamine_liberator': True,
        'dao_blocker': False,
        'safe_serving': '1 small (130g)',
        'moderate_serving': '1 large',
        'high_serving': '2+ oranges',
        'preparation_notes': 'Citrus fruits are histamine liberators. Limit if histamine sensitive.',
        'common_allergens': ''
    },
    {
        'name': 'Avocado',
        'category': 'Fruits',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Amber',
        'histamine_level': 'High',
        'histamine_liberator': True,
        'dao_blocker': False,
        'safe_serving': '1/8 avocado (20g)',
        'moderate_serving': '1/4 avocado',
        'high_serving': '1/2+ avocado',
        'preparation_notes': 'High histamine, especially when ripe. Use very firm/unripe. Sorbitol increases symptoms.',
        'common_allergens': ''
    },

    # VEGETABLES
    {
        'name': 'Carrot',
        'category': 'Vegetables',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Low',
        'histamine_liberator': False,
        'dao_blocker': False,
        'safe_serving': '1 medium (75g)',
        'moderate_serving': '2 medium',
        'high_serving': '3+ medium',
        'preparation_notes': 'Excellent safe vegetable. Both raw and cooked are well tolerated.',
        'common_allergens': ''
    },
    {
        'name': 'Spinach (raw)',
        'category': 'Vegetables',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Very High',
        'histamine_liberator': False,
        'dao_blocker': True,
        'safe_serving': '1 cup (30g)',
        'moderate_serving': '2 cups',
        'high_serving': '3+ cups',
        'preparation_notes': 'Very high histamine. DAO blocker. Avoid if histamine sensitive. Cook to reduce histamine slightly.',
        'common_allergens': ''
    },
    {
        'name': 'Broccoli',
        'category': 'Vegetables',
        'fructans': 'Amber',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Low',
        'histamine_liberator': False,
        'dao_blocker': False,
        'safe_serving': '1/2 cup (75g)',
        'moderate_serving': '3/4 cup',
        'high_serving': '1+ cup',
        'preparation_notes': 'Heads are safer than stems. Limit to moderate serving to avoid FODMAP issues.',
        'common_allergens': ''
    },
    {
        'name': 'Tomato',
        'category': 'Vegetables',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Very High',
        'histamine_liberator': True,
        'dao_blocker': False,
        'safe_serving': 'Avoid if sensitive',
        'moderate_serving': '1 small (fresh only)',
        'high_serving': 'Not recommended',
        'preparation_notes': 'Very high histamine, especially cooked or canned. Sauce/paste highest. Avoid if histamine sensitive.',
        'common_allergens': ''
    },
    {
        'name': 'Lettuce (iceberg)',
        'category': 'Vegetables',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Low',
        'histamine_liberator': False,
        'dao_blocker': False,
        'safe_serving': '2 cups (150g)',
        'moderate_serving': '3 cups',
        'high_serving': 'Unlimited',
        'preparation_notes': 'One of the safest vegetables. Very well tolerated.',
        'common_allergens': ''
    },
    {
        'name': 'Onion (brown)',
        'category': 'Vegetables',
        'fructans': 'Red',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Moderate',
        'histamine_liberator': False,
        'dao_blocker': False,
        'safe_serving': 'Avoid',
        'moderate_serving': 'Avoid',
        'high_serving': 'Avoid',
        'preparation_notes': 'Very high in fructans. Use green onion tops or asafoetida powder instead.',
        'common_allergens': ''
    },
    {
        'name': 'Spring Onion (green tops only)',
        'category': 'Vegetables',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Low',
        'histamine_liberator': False,
        'dao_blocker': False,
        'safe_serving': '2 tablespoons chopped',
        'moderate_serving': '4 tablespoons',
        'high_serving': '1/2 cup',
        'preparation_notes': 'Green parts only - white parts are high FODMAP. Great onion substitute.',
        'common_allergens': ''
    },
    {
        'name': 'Garlic',
        'category': 'Vegetables',
        'fructans': 'Red',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Moderate',
        'histamine_liberator': False,
        'dao_blocker': False,
        'safe_serving': 'Avoid',
        'moderate_serving': 'Avoid',
        'high_serving': 'Avoid',
        'preparation_notes': 'Extremely high in fructans. Use garlic-infused oil instead (FODMAPs not oil soluble, flavor transfers).',
        'common_allergens': ''
    },

    # GRAINS
    {
        'name': 'White Rice (cooked)',
        'category': 'Grains',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Low',
        'histamine_liberator': False,
        'dao_blocker': False,
        'safe_serving': '1 cup (175g)',
        'moderate_serving': '1.5 cups',
        'high_serving': '2+ cups',
        'preparation_notes': 'Excellent safe grain. Well tolerated by most.',
        'common_allergens': ''
    },
    {
        'name': 'Oats (rolled)',
        'category': 'Grains',
        'fructans': 'Amber',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Low',
        'histamine_liberator': False,
        'dao_blocker': False,
        'safe_serving': '1/2 cup dry (52g)',
        'moderate_serving': '3/4 cup',
        'high_serving': '1+ cup',
        'preparation_notes': 'Moderate fructans. Stick to recommended serving. Choose certified gluten-free if needed.',
        'common_allergens': 'May contain gluten from cross-contamination'
    },
    {
        'name': 'Quinoa (cooked)',
        'category': 'Grains',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Low',
        'histamine_liberator': False,
        'dao_blocker': False,
        'safe_serving': '1 cup (155g)',
        'moderate_serving': '1.5 cups',
        'high_serving': '2+ cups',
        'preparation_notes': 'Excellent gluten-free grain alternative. Rinse well before cooking.',
        'common_allergens': ''
    },
    {
        'name': 'Wheat Bread',
        'category': 'Grains',
        'fructans': 'Red',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Moderate',
        'histamine_liberator': False,
        'dao_blocker': False,
        'safe_serving': 'Avoid',
        'moderate_serving': 'Avoid',
        'high_serving': 'Avoid',
        'preparation_notes': 'High fructans. Use sourdough (spelt) or gluten-free bread instead.',
        'common_allergens': 'Gluten'
    },
    {
        'name': 'Sourdough Bread (spelt)',
        'category': 'Grains',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Low',
        'histamine_liberator': False,
        'dao_blocker': False,
        'safe_serving': '2 slices',
        'moderate_serving': '3 slices',
        'high_serving': '4+ slices',
        'preparation_notes': 'Fermentation breaks down fructans. Must be authentic sourdough (24hr+ ferment).',
        'common_allergens': 'Gluten'
    },

    # PROTEINS
    {
        'name': 'Chicken Breast (fresh)',
        'category': 'Proteins',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Low',
        'histamine_liberator': False,
        'dao_blocker': False,
        'safe_serving': '100-150g',
        'moderate_serving': '200g',
        'high_serving': '300g+',
        'preparation_notes': 'Must be very fresh. Cook immediately or freeze. Histamine increases with age.',
        'common_allergens': ''
    },
    {
        'name': 'Eggs',
        'category': 'Proteins',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Low',
        'histamine_liberator': False,
        'dao_blocker': False,
        'safe_serving': '2 eggs',
        'moderate_serving': '3 eggs',
        'high_serving': '4+ eggs',
        'preparation_notes': 'Very fresh eggs best. Well tolerated by most. Avoid if egg white sensitive.',
        'common_allergens': 'Eggs'
    },
    {
        'name': 'Salmon (fresh)',
        'category': 'Proteins',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'High',
        'histamine_liberator': False,
        'dao_blocker': False,
        'safe_serving': 'Very fresh only - 100g',
        'moderate_serving': '150g',
        'high_serving': 'Avoid if sensitive',
        'preparation_notes': 'Fish accumulates histamine rapidly. Must be caught and frozen immediately. Avoid if not ultra-fresh.',
        'common_allergens': 'Fish'
    },
    {
        'name': 'Tuna (canned)',
        'category': 'Proteins',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Very High',
        'histamine_liberator': False,
        'dao_blocker': False,
        'safe_serving': 'Avoid if histamine sensitive',
        'moderate_serving': 'Not recommended',
        'high_serving': 'Avoid',
        'preparation_notes': 'Canned fish very high in histamine. One of worst offenders. Avoid if histamine sensitive.',
        'common_allergens': 'Fish'
    },
    {
        'name': 'Tofu (firm)',
        'category': 'Proteins',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Moderate',
        'histamine_liberator': False,
        'dao_blocker': False,
        'safe_serving': '170g (2/3 cup)',
        'moderate_serving': '250g',
        'high_serving': '350g+',
        'preparation_notes': 'Fermented soy products higher in histamine. Plain tofu better than tempeh.',
        'common_allergens': 'Soy'
    },

    # DAIRY
    {
        'name': 'Cows Milk',
        'category': 'Dairy',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Red',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'High',
        'histamine_liberator': False,
        'dao_blocker': False,
        'safe_serving': 'Avoid if lactose intolerant',
        'moderate_serving': '1/2 cup',
        'high_serving': 'Not recommended',
        'preparation_notes': 'High lactose. Use lactose-free milk or alternatives (almond, oat).',
        'common_allergens': 'Dairy, Lactose'
    },
    {
        'name': 'Lactose-Free Milk',
        'category': 'Dairy',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Moderate',
        'histamine_liberator': False,
        'dao_blocker': False,
        'safe_serving': '1 cup',
        'moderate_serving': '2 cups',
        'high_serving': '3+ cups',
        'preparation_notes': 'Lactose removed. Still contains dairy proteins. Use fresh.',
        'common_allergens': 'Dairy (not lactose)'
    },
    {
        'name': 'Cheddar Cheese (aged)',
        'category': 'Dairy',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Very High',
        'histamine_liberator': False,
        'dao_blocker': True,
        'safe_serving': 'Avoid if histamine sensitive',
        'moderate_serving': '20g',
        'high_serving': 'Avoid',
        'preparation_notes': 'Aged cheeses extremely high in histamine. Fresh cheeses (cream cheese, ricotta) better.',
        'common_allergens': 'Dairy'
    },
    {
        'name': 'Greek Yogurt (plain)',
        'category': 'Dairy',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Moderate',
        'histamine_liberator': False,
        'dao_blocker': False,
        'safe_serving': '1/2 cup',
        'moderate_serving': '3/4 cup',
        'high_serving': '1+ cup',
        'preparation_notes': 'Fermentation reduces lactose but increases histamine. Choose fresh, avoid flavored.',
        'common_allergens': 'Dairy'
    },

    # NUTS & SEEDS
    {
        'name': 'Almonds',
        'category': 'Nuts & Seeds',
        'fructans': 'Amber',
        'gos': 'Amber',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Low',
        'histamine_liberator': False,
        'dao_blocker': False,
        'safe_serving': '10 nuts',
        'moderate_serving': '15 nuts',
        'high_serving': '20+ nuts',
        'preparation_notes': 'Moderate FODMAPs in larger amounts. Almond milk better tolerated than whole nuts.',
        'common_allergens': 'Tree Nuts'
    },
    {
        'name': 'Walnuts',
        'category': 'Nuts & Seeds',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Very High',
        'histamine_liberator': False,
        'dao_blocker': True,
        'safe_serving': '10 halves',
        'moderate_serving': '15 halves',
        'high_serving': 'Avoid if sensitive',
        'preparation_notes': 'High histamine especially if not fresh. DAO blocker. Store in freezer.',
        'common_allergens': 'Tree Nuts'
    },
    {
        'name': 'Cashews',
        'category': 'Nuts & Seeds',
        'fructans': 'Red',
        'gos': 'Red',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'High',
        'histamine_liberator': True,
        'dao_blocker': False,
        'safe_serving': 'Avoid',
        'moderate_serving': 'Avoid',
        'high_serving': 'Avoid',
        'preparation_notes': 'High FODMAPs AND high histamine. Double trigger. Avoid.',
        'common_allergens': 'Tree Nuts'
    },
    {
        'name': 'Peanuts',
        'category': 'Nuts & Seeds',
        'fructans': 'Amber',
        'gos': 'Amber',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Very High',
        'histamine_liberator': True,
        'dao_blocker': False,
        'safe_serving': '15 nuts',
        'moderate_serving': 'Avoid if histamine sensitive',
        'high_serving': 'Avoid',
        'preparation_notes': 'High histamine liberator. Peanut butter even worse. Often moldy (adds histamine).',
        'common_allergens': 'Peanuts'
    },
    {
        'name': 'Chia Seeds',
        'category': 'Nuts & Seeds',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Low',
        'histamine_liberator': False,
        'dao_blocker': False,
        'safe_serving': '2 tablespoons',
        'moderate_serving': '3 tablespoons',
        'high_serving': '4+ tablespoons',
        'preparation_notes': 'Excellent safe seed. Good fiber source. Soak before eating for easier digestion.',
        'common_allergens': ''
    },

    # BEVERAGES
    {
        'name': 'Coffee (brewed)',
        'category': 'Beverages',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'High',
        'histamine_liberator': True,
        'dao_blocker': True,
        'safe_serving': '1 cup (weak)',
        'moderate_serving': '2 cups',
        'high_serving': 'Avoid if sensitive',
        'preparation_notes': 'High histamine liberator and DAO blocker. Can trigger symptoms. Limit or avoid.',
        'common_allergens': ''
    },
    {
        'name': 'Black Tea',
        'category': 'Beverages',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Moderate',
        'histamine_liberator': False,
        'dao_blocker': True,
        'safe_serving': '1-2 cups (weak)',
        'moderate_serving': '3 cups',
        'high_serving': 'Not recommended',
        'preparation_notes': 'DAO blocker. Green tea slightly better. Herbal teas (peppermint, ginger) best choice.',
        'common_allergens': ''
    },
    {
        'name': 'Peppermint Tea',
        'category': 'Beverages',
        'fructans': 'Green',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Green',
        'polyols': 'Green',
        'histamine_level': 'Low',
        'histamine_liberator': False,
        'dao_blocker': False,
        'safe_serving': 'Unlimited',
        'moderate_serving': 'Unlimited',
        'high_serving': 'Unlimited',
        'preparation_notes': 'Excellent for gut health. Helps with IBS symptoms. Safe choice.',
        'common_allergens': ''
    },
    {
        'name': 'Alcohol (wine, beer)',
        'category': 'Beverages',
        'fructans': 'Red',
        'gos': 'Green',
        'lactose': 'Green',
        'fructose': 'Amber',
        'polyols': 'Green',
        'histamine_level': 'Very High',
        'histamine_liberator': True,
        'dao_blocker': True,
        'safe_serving': 'Avoid',
        'moderate_serving': 'Avoid',
        'high_serving': 'Avoid',
        'preparation_notes': 'High histamine, DAO blocker, histamine liberator. Triple trigger. Major symptom trigger.',
        'common_allergens': ''
    },
]

def seed_foods():
    """Add sample foods to database"""
    with app.app_context():
        # Check if foods already exist
        existing_count = Food.query.count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} foods.")
            response = input("Do you want to add more foods anyway? (yes/no): ")
            if response.lower() != 'yes':
                print("Seeding cancelled.")
                return

        print(f"Adding {len(SAMPLE_FOODS)} foods to database...")

        added = 0
        for food_data in SAMPLE_FOODS:
            # Check if food already exists
            existing = Food.query.filter_by(name=food_data['name']).first()
            if existing:
                print(f"  Skipping '{food_data['name']}' - already exists")
                continue

            food = Food(**food_data)
            db.session.add(food)
            added += 1
            print(f"  Added: {food_data['name']}")

        db.session.commit()

        total = Food.query.count()
        print(f"\n[OK] Successfully added {added} new foods!")
        print(f"[OK] Total foods in database: {total}")
        print("\nYou can now search for foods in the application!")

if __name__ == '__main__':
    seed_foods()
