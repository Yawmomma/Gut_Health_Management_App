"""
Fix USDA links for existing foods
==================================
This script finds foods in the FODMAP database that don't have USDA links
but match USDA food names, and adds the links.
"""
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database import db
from models.food import Food
from models.usda import USDAFood

def main():
    print("\n" + "=" * 70)
    print("FIX USDA LINKS FOR EXISTING FOODS")
    print("=" * 70)

    with app.app_context():
        # Get foods without USDA links
        foods_without_links = Food.query.filter(Food.usda_food_id.is_(None)).all()
        print(f"\nFound {len(foods_without_links):,} foods without USDA links")

        # Confirm before proceeding
        confirm = input("\nSearch for matching USDA foods and add links? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Cancelled.")
            return

        print("\n[...] Searching for matches...")

        matched = 0
        not_matched = 0
        batch_size = 100

        for i, food in enumerate(foods_without_links):
            # Try to find exact match in USDA database
            usda_food = USDAFood.query.filter_by(description=food.name).first()

            if usda_food:
                food.usda_food_id = usda_food.id
                matched += 1
            else:
                not_matched += 1

            # Commit in batches
            if (i + 1) % batch_size == 0:
                db.session.commit()
                progress = ((i + 1) / len(foods_without_links)) * 100
                print(f"  Progress: {i + 1}/{len(foods_without_links)} ({progress:.1f}%) - Matched: {matched}, Not matched: {not_matched}")

        # Final commit
        db.session.commit()

        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)
        print(f"Foods processed:      {len(foods_without_links):,}")
        print(f"Links added:          {matched:,}")
        print(f"No match found:       {not_matched:,}")
        print("=" * 70)

        # Verify
        total_with_links = Food.query.filter(Food.usda_food_id.isnot(None)).count()
        print(f"\nTotal foods with USDA links now: {total_with_links:,}")
        print("\n[OK] Links updated successfully!")

if __name__ == '__main__':
    main()
