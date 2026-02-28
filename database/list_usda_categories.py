"""
Quick script to list all USDA categories with food counts
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models.usda import USDAFoodCategory

def main():
    with app.app_context():
        categories = USDAFoodCategory.query.order_by(USDAFoodCategory.description).all()

        print("\n" + "=" * 70)
        print("USDA FOOD CATEGORIES")
        print("=" * 70)
        print(f"{'Category':<50} {'Food Count':>15}")
        print("-" * 70)

        for cat in categories:
            print(f"{cat.description:<50} {cat.food_count:>15,}")

        print("-" * 70)
        print(f"{'TOTAL CATEGORIES:':<50} {len(categories):>15}")
        print("=" * 70)

if __name__ == '__main__':
    main()
