"""
Copy fresh foods from USDA database to FODMAP database
=======================================================
This script copies food items from the USDA database to the Foods table (FODMAP compendium).
It creates basic food entries with name, category, and a link to the USDA database for
nutritional information. All FODMAP/histamine fields are left empty for manual entry.

Usage:
    python database/copy_usda_to_fodmap.py

The script will:
1. Ask which categories you want to copy
2. Copy foods from those categories to the Foods table
3. Link each food to its USDA entry (usda_food_id) for nutritional data
4. Skip foods that already exist in the Foods table (by name match)

Benefits:
- No data duplication - nutritional info stays in USDA database
- FODMAP foods link to USDA foods via usda_food_id foreign key
- Access USDA nutritional data via food.usda_food relationship
"""
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database import db
from models.usda import USDAFoodCategory, USDAFood
from models.food import Food


# Recommended fresh food categories
FRESH_FOOD_CATEGORIES = [
    'Fruits and Fruit Juices',
    'Vegetables and Vegetable Products',
    'Dairy and Egg Products',
    'Finfish and Shellfish Products',
    'Beef Products',
    'Pork Products',
    'Poultry Products',
    'Lamb, Veal, and Game Products',
    'Nut and Seed Products',
    'Legumes and Legume Products',
    'Cereal Grains and Pasta',
    'Spices and Herbs',
]


def list_categories():
    """List all USDA categories with food counts"""
    categories = USDAFoodCategory.query.order_by(USDAFoodCategory.description).all()

    print("\n" + "=" * 70)
    print("AVAILABLE USDA CATEGORIES")
    print("=" * 70)
    print(f"{'#':<4} {'Category':<50} {'Foods':>10}")
    print("-" * 70)

    for i, cat in enumerate(categories, 1):
        marker = "*" if cat.description in FRESH_FOOD_CATEGORIES else " "
        print(f"{i:<3}{marker} {cat.description:<50} {cat.food_count:>10,}")

    print("-" * 70)
    print("* = Recommended fresh food categories")
    print("=" * 70)

    return categories


def get_category_selection(categories):
    """Ask user which categories to copy"""
    print("\nOptions:")
    print("  1. Copy ALL recommended fresh food categories (marked with *)")
    print("  2. Copy ALL categories")
    print("  3. Select specific categories")
    print("  4. Enter category numbers (comma-separated)")

    choice = input("\nYour choice (1-4): ").strip()

    if choice == '1':
        # Return recommended categories
        return [c for c in categories if c.description in FRESH_FOOD_CATEGORIES]
    elif choice == '2':
        # Return all categories
        return categories
    elif choice == '3':
        # Let user select specific categories
        print("\nEnter category names (one per line, empty line to finish):")
        selected = []
        while True:
            name = input("> ").strip()
            if not name:
                break
            matches = [c for c in categories if name.lower() in c.description.lower()]
            if matches:
                selected.extend(matches)
                print(f"  Added: {', '.join(c.description for c in matches)}")
            else:
                print(f"  No match found for: {name}")
        return selected
    elif choice == '4':
        # Let user enter numbers
        numbers = input("Enter category numbers (comma-separated): ").strip()
        selected = []
        for num_str in numbers.split(','):
            try:
                num = int(num_str.strip())
                if 1 <= num <= len(categories):
                    selected.append(categories[num - 1])
            except ValueError:
                pass
        return selected
    else:
        print("Invalid choice. Using recommended categories.")
        return [c for c in categories if c.description in FRESH_FOOD_CATEGORIES]


def copy_foods_from_category(category):
    """Copy all foods from a USDA category to the FODMAP database"""
    print(f"\n[...] Processing category: {category.description}")

    # Get all foods in this category
    usda_foods = USDAFood.query.filter_by(category_id=category.id).all()
    print(f"     Found {len(usda_foods)} foods in USDA database")

    copied = 0
    skipped = 0
    batch_size = 100

    for i, usda_food in enumerate(usda_foods):
        # Check if food already exists in FODMAP database (by name)
        existing = Food.query.filter_by(name=usda_food.description).first()
        if existing:
            skipped += 1
            continue

        # Create new food entry with link to USDA database
        # All FODMAP/histamine fields will be NULL (empty)
        new_food = Food(
            name=usda_food.description,
            category=category.description,
            usda_food_id=usda_food.id,  # Link to USDA food for nutritional info
            # All FODMAP and histamine fields are left NULL/empty
            # User will fill these in later
        )

        db.session.add(new_food)
        copied += 1

        # Commit in batches
        if (i + 1) % batch_size == 0:
            db.session.commit()

    # Final commit
    db.session.commit()

    print(f"[OK] Copied {copied} foods, skipped {skipped} duplicates")
    return copied, skipped


def main():
    """Main function"""
    print("=" * 70)
    print("COPY USDA FOODS TO FODMAP DATABASE")
    print("=" * 70)

    with app.app_context():
        # List categories and get user selection
        categories = list_categories()
        selected_categories = get_category_selection(categories)

        if not selected_categories:
            print("\n[ERROR] No categories selected!")
            return

        print(f"\n[OK] Selected {len(selected_categories)} categories:")
        for cat in selected_categories:
            print(f"     - {cat.description} ({cat.food_count} foods)")

        # Confirm
        confirm = input("\nProceed with copying? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Cancelled.")
            return

        # Copy foods from each category
        total_copied = 0
        total_skipped = 0

        for category in selected_categories:
            copied, skipped = copy_foods_from_category(category)
            total_copied += copied
            total_skipped += skipped

        # Print summary
        print("\n" + "=" * 70)
        print("COPY SUMMARY")
        print("=" * 70)
        print(f"Categories processed: {len(selected_categories)}")
        print(f"Foods copied:         {total_copied:,}")
        print(f"Duplicates skipped:   {total_skipped:,}")
        print(f"Total foods in FODMAP database: {Food.query.count():,}")
        print("=" * 70)
        print("\n[OK] Copy completed successfully!")
        print("\nNext steps:")
        print("  1. Go to Food Compendium in the app")
        print("  2. Edit each food to add FODMAP and histamine ratings")
        print("  3. Add serving sizes as needed")
        print("\nNote: Nutritional information is linked via usda_food_id")
        print("      Access USDA data using food.usda_food relationship")


if __name__ == '__main__':
    main()
