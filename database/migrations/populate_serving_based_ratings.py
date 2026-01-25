"""
Migration script to populate serving-based ratings from legacy fields
For existing food records that don't have serving-based ratings,
copy the legacy single ratings to the safe serving level.
"""
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import app
from database import db
from models.food import Food

def upgrade():
    """Populate serving-based ratings from legacy fields"""
    with app.app_context():
        print("Populating serving-based ratings from legacy fields...")

        # Get all foods
        foods = Food.query.all()
        updated_count = 0

        for food in foods:
            updated = False

            # Update safe serving FODMAP ratings if they're None
            if food.safe_fructans is None:
                food.safe_fructans = food.fructans if food.fructans is not None else 'Green'
                updated = True
            if food.safe_gos is None:
                food.safe_gos = food.gos if food.gos is not None else 'Green'
                updated = True
            if food.safe_lactose is None:
                food.safe_lactose = food.lactose if food.lactose is not None else 'Green'
                updated = True
            if food.safe_fructose is None:
                food.safe_fructose = food.fructose if food.fructose is not None else 'Green'
                updated = True
            if food.safe_polyols is None:
                food.safe_polyols = food.polyols if food.polyols is not None else 'Green'
                updated = True
            if food.safe_mannitol is None:
                food.safe_mannitol = food.mannitol if food.mannitol is not None else 'Green'
                updated = True
            if food.safe_sorbitol is None:
                food.safe_sorbitol = food.sorbitol if food.sorbitol is not None else 'Green'
                updated = True

            # Update safe serving histamine ratings if they're None or invalid
            if food.safe_histamine_level is None:
                food.safe_histamine_level = food.histamine_level if food.histamine_level is not None else 'Low'
                updated = True

            # Convert 0 to 'No' for histamine liberator and dao blocker
            if food.safe_histamine_liberator is None or food.safe_histamine_liberator == '0' or food.safe_histamine_liberator == 0:
                if food.histamine_liberator and food.histamine_liberator not in ['0', 0, None]:
                    food.safe_histamine_liberator = food.histamine_liberator
                else:
                    food.safe_histamine_liberator = 'No'
                updated = True

            if food.safe_dao_blocker is None or food.safe_dao_blocker == '0' or food.safe_dao_blocker == 0:
                if food.dao_blocker and food.dao_blocker not in ['0', 0, None]:
                    food.safe_dao_blocker = food.dao_blocker
                else:
                    food.safe_dao_blocker = 'No'
                updated = True

            # Set defaults for moderate serving if None (Amber/Medium/No)
            if food.moderate_fructans is None:
                food.moderate_fructans = 'Amber'
                updated = True
            if food.moderate_gos is None:
                food.moderate_gos = 'Amber'
                updated = True
            if food.moderate_lactose is None:
                food.moderate_lactose = 'Amber'
                updated = True
            if food.moderate_fructose is None:
                food.moderate_fructose = 'Amber'
                updated = True
            if food.moderate_polyols is None:
                food.moderate_polyols = 'Amber'
                updated = True
            if food.moderate_mannitol is None:
                food.moderate_mannitol = 'Amber'
                updated = True
            if food.moderate_sorbitol is None:
                food.moderate_sorbitol = 'Amber'
                updated = True
            if food.moderate_histamine_level is None:
                food.moderate_histamine_level = 'Medium'
                updated = True
            if food.moderate_histamine_liberator is None:
                food.moderate_histamine_liberator = 'No'
                updated = True
            if food.moderate_dao_blocker is None:
                food.moderate_dao_blocker = 'No'
                updated = True

            # Set defaults for high serving if None (Red/High/Yes)
            if food.high_fructans is None:
                food.high_fructans = 'Red'
                updated = True
            if food.high_gos is None:
                food.high_gos = 'Red'
                updated = True
            if food.high_lactose is None:
                food.high_lactose = 'Red'
                updated = True
            if food.high_fructose is None:
                food.high_fructose = 'Red'
                updated = True
            if food.high_polyols is None:
                food.high_polyols = 'Red'
                updated = True
            if food.high_mannitol is None:
                food.high_mannitol = 'Red'
                updated = True
            if food.high_sorbitol is None:
                food.high_sorbitol = 'Red'
                updated = True
            if food.high_histamine_level is None:
                food.high_histamine_level = 'High'
                updated = True
            if food.high_histamine_liberator is None:
                food.high_histamine_liberator = 'Yes'
                updated = True
            if food.high_dao_blocker is None:
                food.high_dao_blocker = 'Yes'
                updated = True

            if updated:
                updated_count += 1
                print(f"✓ Updated: {food.name}")

        db.session.commit()
        print(f"\n✓ Migration completed successfully!")
        print(f"Updated {updated_count} food records with serving-based ratings.")

if __name__ == '__main__':
    print("=" * 60)
    print("POPULATE SERVING-BASED RATINGS MIGRATION")
    print("=" * 60)
    upgrade()
