"""
Interactive script to link manually-entered foods to USDA foods
================================================================
This script shows foods without USDA links and helps you find and
link them to matching USDA foods.
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

def search_usda_foods(query, limit=5):
    """Search USDA foods by name (case-insensitive partial match)"""
    return USDAFood.query.filter(
        USDAFood.description.ilike(f'%{query}%')
    ).limit(limit).all()

def main():
    print("\n" + "=" * 70)
    print("LINK MANUAL FOODS TO USDA FOODS")
    print("=" * 70)

    with app.app_context():
        # Get foods without USDA links
        foods_without_links = Food.query.filter(Food.usda_food_id.is_(None)).all()

        if not foods_without_links:
            print("\n[OK] All foods already have USDA links!")
            return

        print(f"\nFound {len(foods_without_links)} foods without USDA links")
        print("\nFor each food, you can:")
        print("  - Enter a number to select a matching USDA food")
        print("  - Press Enter to search with a different term")
        print("  - Type 's' to skip this food")
        print("  - Type 'q' to quit")

        linked_count = 0

        for i, food in enumerate(foods_without_links, 1):
            print("\n" + "=" * 70)
            print(f"[{i}/{len(foods_without_links)}] Food: {food.name}")
            print(f"Category: {food.category}")
            print("=" * 70)

            # Try to find matches with the food name
            matches = search_usda_foods(food.name, limit=5)

            while True:
                if matches:
                    print("\nPossible USDA matches:")
                    for j, match in enumerate(matches, 1):
                        category_str = f" ({match.category.description})" if match.category else ""
                        print(f"  {j}. {match.description}{category_str}")
                else:
                    print("\nNo matches found.")

                choice = input("\nSelect option (1-5, Enter=search, s=skip, q=quit): ").strip().lower()

                if choice == 'q':
                    print("\nQuitting...")
                    print(f"Linked {linked_count} foods")
                    return
                elif choice == 's':
                    print("Skipped.")
                    break
                elif choice == '':
                    search_term = input("Enter search term: ").strip()
                    if search_term:
                        matches = search_usda_foods(search_term, limit=5)
                    continue
                elif choice.isdigit() and 1 <= int(choice) <= len(matches):
                    selected = matches[int(choice) - 1]
                    food.usda_food_id = selected.id
                    db.session.commit()
                    print(f"✓ Linked to: {selected.description}")
                    linked_count += 1
                    break
                else:
                    print("Invalid choice. Try again.")

        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Foods linked: {linked_count}")
        print(f"Foods remaining without links: {len(foods_without_links) - linked_count}")
        print("=" * 70)

        total_with_links = Food.query.filter(Food.usda_food_id.isnot(None)).count()
        print(f"\nTotal foods with USDA links: {total_with_links:,}")

if __name__ == '__main__':
    main()
