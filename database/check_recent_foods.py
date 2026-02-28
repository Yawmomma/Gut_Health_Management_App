"""
Check recently added foods
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models.food import Food

def main():
    with app.app_context():
        # Get foods added in the last 24 hours
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_foods = Food.query.filter(Food.created_at >= yesterday).order_by(Food.created_at.desc()).all()

        print("\n" + "=" * 70)
        print("RECENTLY ADDED FOODS (Last 24 hours)")
        print("=" * 70)
        print(f"Total recent foods: {len(recent_foods)}")

        if recent_foods:
            with_usda = sum(1 for f in recent_foods if f.usda_food_id is not None)
            without_usda = sum(1 for f in recent_foods if f.usda_food_id is None)

            print(f"  - With USDA link:    {with_usda}")
            print(f"  - Without USDA link: {without_usda}")
            print("\nFirst 10 recent foods:")
            for i, food in enumerate(recent_foods[:10], 1):
                usda_status = f"USDA ID: {food.usda_food_id}" if food.usda_food_id else "NO USDA LINK"
                print(f"  {i}. {food.name} - {usda_status}")
        else:
            print("No foods added in the last 24 hours")

        print("=" * 70)

if __name__ == '__main__':
    main()
