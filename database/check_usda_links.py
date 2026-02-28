"""
Quick check to see if foods have USDA links
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models.food import Food

def main():
    with app.app_context():
        total_foods = Food.query.count()
        foods_with_usda = Food.query.filter(Food.usda_food_id.isnot(None)).count()
        foods_without_usda = Food.query.filter(Food.usda_food_id.is_(None)).count()

        print("\n" + "=" * 60)
        print("USDA LINK STATUS")
        print("=" * 60)
        print(f"Total foods in FODMAP database:     {total_foods:,}")
        print(f"Foods with USDA link:                {foods_with_usda:,}")
        print(f"Foods without USDA link:             {foods_without_usda:,}")
        print("=" * 60)

        if foods_with_usda > 0:
            print("\nSample foods with USDA links:")
            sample = Food.query.filter(Food.usda_food_id.isnot(None)).limit(5).all()
            for food in sample:
                print(f"  - {food.name} (ID: {food.id}, USDA ID: {food.usda_food_id})")

        if foods_without_usda > 0:
            print("\nSample foods without USDA links:")
            sample = Food.query.filter(Food.usda_food_id.is_(None)).limit(5).all()
            for food in sample:
                print(f"  - {food.name} (ID: {food.id})")

        print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
