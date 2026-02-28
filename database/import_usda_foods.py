"""
USDA FoodData Central Import Script
====================================
Imports food data from USDA JSON files (Foundation, SR Legacy, Survey/FNDDS, Branded).

Usage:
    1. Download JSON files from https://fdc.nal.usda.gov/download-datasets
    2. Place them in data/usda/ folder:
       - FoodData_Central_foundation_food_json_YYYY-MM-DD.json
       - FoodData_Central_sr_legacy_food_json_YYYY-MM-DD.json
       - surveyDownload.json (FNDDS/Survey foods)
       - FoodData_Central_branded_food_json_YYYY-MM-DD.json (WARNING: Very large file ~3GB)
    3. Run: python database/import_usda_foods.py

The script is idempotent - safe to run multiple times.

Note: Branded foods file is very large and may take significant time to import.
"""

import sys
import os
import json
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database import db
from models.usda import USDAFoodCategory, USDAFood, USDANutrient, USDAFoodNutrient, USDAFoodPortion


# Nutrient group mappings based on USDA nutrient IDs
NUTRIENT_GROUPS = {
    # Energy
    1008: 'Energy', 2047: 'Energy', 2048: 'Energy',
    # Proximates (macros)
    1003: 'Proximates', 1004: 'Proximates', 1005: 'Proximates', 1009: 'Proximates',
    1079: 'Proximates', 1051: 'Proximates', 1010: 'Proximates', 1011: 'Proximates',
    1012: 'Proximates', 1013: 'Proximates', 1050: 'Proximates', 1063: 'Proximates',
    1057: 'Proximates', 1058: 'Proximates', 1018: 'Proximates', 1002: 'Proximates',
    # Minerals
    1087: 'Minerals', 1089: 'Minerals', 1090: 'Minerals', 1091: 'Minerals',
    1092: 'Minerals', 1093: 'Minerals', 1094: 'Minerals', 1095: 'Minerals',
    1096: 'Minerals', 1097: 'Minerals', 1098: 'Minerals', 1099: 'Minerals',
    1100: 'Minerals', 1101: 'Minerals', 1102: 'Minerals', 1103: 'Minerals',
    1137: 'Minerals', 1146: 'Minerals', 1180: 'Minerals',
    # Vitamins
    1104: 'Vitamins', 1105: 'Vitamins', 1106: 'Vitamins', 1107: 'Vitamins',
    1108: 'Vitamins', 1109: 'Vitamins', 1110: 'Vitamins', 1111: 'Vitamins',
    1114: 'Vitamins', 1116: 'Vitamins', 1117: 'Vitamins', 1118: 'Vitamins',
    1119: 'Vitamins', 1120: 'Vitamins', 1121: 'Vitamins', 1122: 'Vitamins',
    1123: 'Vitamins', 1124: 'Vitamins', 1125: 'Vitamins', 1126: 'Vitamins',
    1127: 'Vitamins', 1128: 'Vitamins', 1129: 'Vitamins', 1130: 'Vitamins',
    1131: 'Vitamins', 1162: 'Vitamins', 1165: 'Vitamins', 1166: 'Vitamins',
    1167: 'Vitamins', 1170: 'Vitamins', 1175: 'Vitamins', 1176: 'Vitamins',
    1177: 'Vitamins', 1178: 'Vitamins', 1183: 'Vitamins', 1184: 'Vitamins',
    1185: 'Vitamins', 1186: 'Vitamins', 1187: 'Vitamins', 1188: 'Vitamins',
    1190: 'Vitamins', 1191: 'Vitamins', 1192: 'Vitamins', 1246: 'Vitamins',
    # Lipids
    1253: 'Lipids', 1257: 'Lipids', 1258: 'Lipids', 1259: 'Lipids',
    1260: 'Lipids', 1261: 'Lipids', 1262: 'Lipids', 1263: 'Lipids',
    1264: 'Lipids', 1265: 'Lipids', 1266: 'Lipids', 1267: 'Lipids',
    1268: 'Lipids', 1269: 'Lipids', 1270: 'Lipids', 1271: 'Lipids',
    1272: 'Lipids', 1273: 'Lipids', 1274: 'Lipids', 1275: 'Lipids',
    1276: 'Lipids', 1277: 'Lipids', 1278: 'Lipids', 1279: 'Lipids',
    1280: 'Lipids', 1292: 'Lipids', 1293: 'Lipids', 1310: 'Lipids',
    1311: 'Lipids', 1312: 'Lipids', 1313: 'Lipids', 1314: 'Lipids',
    1315: 'Lipids', 1316: 'Lipids', 1317: 'Lipids', 1321: 'Lipids',
    1323: 'Lipids', 1325: 'Lipids', 1329: 'Lipids', 1330: 'Lipids',
    1331: 'Lipids', 1332: 'Lipids', 1333: 'Lipids',
    # Amino Acids
    1210: 'Amino Acids', 1211: 'Amino Acids', 1212: 'Amino Acids', 1213: 'Amino Acids',
    1214: 'Amino Acids', 1215: 'Amino Acids', 1216: 'Amino Acids', 1217: 'Amino Acids',
    1218: 'Amino Acids', 1219: 'Amino Acids', 1220: 'Amino Acids', 1221: 'Amino Acids',
    1222: 'Amino Acids', 1223: 'Amino Acids', 1224: 'Amino Acids', 1225: 'Amino Acids',
    1226: 'Amino Acids', 1227: 'Amino Acids', 1232: 'Amino Acids', 1233: 'Amino Acids',
    1234: 'Amino Acids',
    # Other
    1253: 'Lipids', 1007: 'Other', 1008: 'Energy', 1062: 'Other',
}


def find_usda_files():
    """Find USDA JSON files in data/usda/ folder"""
    usda_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'usda')
    usda_dir = os.path.abspath(usda_dir)

    if not os.path.exists(usda_dir):
        print(f"[ERROR] Directory not found: {usda_dir}")
        print("Please create the data/usda/ folder and place USDA JSON files there.")
        return {}

    files = {
        'foundation': None,
        'sr_legacy': None,
        'survey': None,
        'branded': None
    }

    for filename in os.listdir(usda_dir):
        filepath = os.path.join(usda_dir, filename)
        if filename.endswith('.json'):
            # Get file size in MB
            size_mb = os.path.getsize(filepath) / (1024 * 1024)

            if 'foundation' in filename.lower():
                files['foundation'] = filepath
                print(f"[OK] Found Foundation file: {filename} ({size_mb:.1f} MB)")
            elif 'sr_legacy' in filename.lower() or 'srlegacy' in filename.lower():
                files['sr_legacy'] = filepath
                print(f"[OK] Found SR Legacy file: {filename} ({size_mb:.1f} MB)")
            elif 'survey' in filename.lower():
                files['survey'] = filepath
                print(f"[OK] Found Survey/FNDDS file: {filename} ({size_mb:.1f} MB)")
            elif 'branded' in filename.lower():
                files['branded'] = filepath
                print(f"[OK] Found Branded Foods file: {filename} ({size_mb:.1f} MB)")
                if size_mb > 1000:
                    print(f"     WARNING: Large file! Import may take a long time.")

    return files


def load_json_file(filepath):
    """Load and parse a USDA JSON file"""
    print(f"\n[...] Loading {os.path.basename(filepath)}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def import_categories(foods_data):
    """Import unique food categories"""
    print("\n[...] Importing categories...")
    categories_seen = {}

    for food in foods_data:
        food_category = food.get('foodCategory', {})
        if food_category:
            # Handle both formats: {id: X, description: Y} and {description: Y}
            cat_id = food_category.get('id')
            cat_desc = food_category.get('description', 'Unknown')

            # Use description as key if no id (SR Legacy format)
            if cat_id:
                key = cat_id
            elif cat_desc:
                key = cat_desc
            else:
                continue

            if key not in categories_seen:
                categories_seen[key] = {'id': cat_id, 'description': cat_desc}

    imported = 0
    for key, cat_data in categories_seen.items():
        cat_id = cat_data['id']
        cat_desc = cat_data['description']

        # Check by description if no id, or by id if present
        if cat_id:
            existing = USDAFoodCategory.query.filter_by(usda_category_id=cat_id).first()
        else:
            existing = USDAFoodCategory.query.filter_by(description=cat_desc).first()

        if not existing:
            category = USDAFoodCategory(
                usda_category_id=cat_id,  # May be None for SR Legacy
                description=cat_desc
            )
            db.session.add(category)
            imported += 1

    db.session.commit()
    print(f"[OK] Imported {imported} new categories ({len(categories_seen)} total unique)")
    return categories_seen


def import_nutrients(foods_data):
    """Import unique nutrient definitions"""
    print("\n[...] Importing nutrient definitions...")
    nutrients_seen = {}

    for food in foods_data:
        for fn in food.get('foodNutrients', []):
            nutrient = fn.get('nutrient', {})
            if nutrient:
                nut_id = nutrient.get('id')
                if nut_id and nut_id not in nutrients_seen:
                    nutrients_seen[nut_id] = {
                        'name': nutrient.get('name', 'Unknown'),
                        'unit': nutrient.get('unitName', ''),
                        'rank': nutrient.get('rank', 999)
                    }

    imported = 0
    for nut_id, nut_data in nutrients_seen.items():
        existing = USDANutrient.query.filter_by(nutrient_id=nut_id).first()
        if not existing:
            nutrient = USDANutrient(
                nutrient_id=nut_id,
                name=nut_data['name'],
                unit_name=nut_data['unit'],
                nutrient_group=NUTRIENT_GROUPS.get(nut_id, 'Other'),
                rank=nut_data['rank']
            )
            db.session.add(nutrient)
            imported += 1

    db.session.commit()
    print(f"[OK] Imported {imported} new nutrients ({len(nutrients_seen)} total unique)")
    return nutrients_seen


def import_foods(foods_data, data_type):
    """Import foods with their nutrients and portions"""
    print(f"\n[...] Importing {data_type} foods...")

    # Build lookup dicts for categories and nutrients
    # Support both id-based and description-based lookups
    category_lookup_by_id = {c.usda_category_id: c.id for c in USDAFoodCategory.query.all() if c.usda_category_id}
    category_lookup_by_desc = {c.description: c.id for c in USDAFoodCategory.query.all()}
    nutrient_lookup = {n.nutrient_id: n.id for n in USDANutrient.query.all()}

    total_foods = len(foods_data)
    imported_foods = 0
    skipped_foods = 0
    imported_nutrients = 0
    imported_portions = 0

    # Process in batches
    batch_size = 100

    for i, food_data in enumerate(foods_data):
        fdc_id = food_data.get('fdcId')
        if not fdc_id:
            continue

        # Check if food already exists
        existing = USDAFood.query.filter_by(fdc_id=fdc_id).first()
        if existing:
            skipped_foods += 1
            continue

        # Get category (support both id-based and description-based)
        food_category = food_data.get('foodCategory', {})
        category_id = None
        if food_category:
            usda_cat_id = food_category.get('id')
            cat_desc = food_category.get('description')
            if usda_cat_id:
                category_id = category_lookup_by_id.get(usda_cat_id)
            elif cat_desc:
                category_id = category_lookup_by_desc.get(cat_desc)

        # Create food
        food = USDAFood(
            fdc_id=fdc_id,
            description=food_data.get('description', 'Unknown'),
            data_type=data_type,
            category_id=category_id,
            scientific_name=food_data.get('scientificName'),
            common_names=food_data.get('commonNames'),
            food_class=food_data.get('foodClass'),
            publication_date=food_data.get('publicationDate')
        )
        db.session.add(food)
        db.session.flush()  # Get the food.id

        # Import nutrients for this food
        for fn_data in food_data.get('foodNutrients', []):
            nutrient_info = fn_data.get('nutrient', {})
            nut_id = nutrient_info.get('id')
            if nut_id and nut_id in nutrient_lookup:
                amount = fn_data.get('amount')
                if amount is not None:
                    food_nutrient = USDAFoodNutrient(
                        food_id=food.id,
                        nutrient_id=nutrient_lookup[nut_id],
                        amount=amount
                    )
                    db.session.add(food_nutrient)
                    imported_nutrients += 1

        # Import portions for this food
        for portion_data in food_data.get('foodPortions', []):
            portion = USDAFoodPortion(
                food_id=food.id,
                usda_portion_id=portion_data.get('id'),
                portion_description=portion_data.get('portionDescription'),
                gram_weight=portion_data.get('gramWeight'),
                amount=portion_data.get('amount'),
                modifier=portion_data.get('modifier'),
                measure_unit=portion_data.get('measureUnit', {}).get('name') if isinstance(portion_data.get('measureUnit'), dict) else portion_data.get('measureUnit'),
                sequence_number=portion_data.get('sequenceNumber')
            )
            db.session.add(portion)
            imported_portions += 1

        imported_foods += 1

        # Commit in batches
        if (i + 1) % batch_size == 0:
            db.session.commit()
            progress = ((i + 1) / total_foods) * 100
            print(f"  Progress: {i + 1}/{total_foods} ({progress:.1f}%)")

    # Final commit
    db.session.commit()

    print(f"[OK] Imported {imported_foods} new foods (skipped {skipped_foods} existing)")
    print(f"     {imported_nutrients} nutrient values")
    print(f"     {imported_portions} portions")

    return imported_foods


def update_category_counts():
    """Update food counts for each category"""
    print("\n[...] Updating category food counts...")
    categories = USDAFoodCategory.query.all()
    for cat in categories:
        cat.food_count = USDAFood.query.filter_by(category_id=cat.id).count()
    db.session.commit()
    print("[OK] Category counts updated")


def print_summary():
    """Print import summary"""
    print("\n" + "=" * 60)
    print("IMPORT SUMMARY")
    print("=" * 60)
    print(f"Categories:     {USDAFoodCategory.query.count()}")
    print(f"Nutrients:      {USDANutrient.query.count()}")
    print(f"Foods:          {USDAFood.query.count()}")
    print(f"  - Foundation: {USDAFood.query.filter_by(data_type='Foundation').count()}")
    print(f"  - SR Legacy:  {USDAFood.query.filter_by(data_type='SR Legacy').count()}")
    print(f"  - Survey:     {USDAFood.query.filter_by(data_type='Survey').count()}")
    print(f"  - Branded:    {USDAFood.query.filter_by(data_type='Branded').count()}")
    print(f"Food Nutrients: {USDAFoodNutrient.query.count()}")
    print(f"Portions:       {USDAFoodPortion.query.count()}")
    print("=" * 60)


def main():
    """Main import function"""
    print("=" * 60)
    print("USDA FOODDATA CENTRAL IMPORT")
    print("=" * 60)

    # Find files
    files = find_usda_files()

    if not any(files.values()):
        print("\n[ERROR] No USDA JSON files found!")
        print("\nPlease download JSON files from:")
        print("  https://fdc.nal.usda.gov/download-datasets")
        print("\nAnd place them in:")
        print("  data/usda/")
        return

    with app.app_context():
        all_foods = []

        # Load Foundation Foods
        if files.get('foundation'):
            data = load_json_file(files['foundation'])
            foundation_foods = data.get('FoundationFoods', [])
            print(f"[OK] Loaded {len(foundation_foods)} Foundation foods")
            for food in foundation_foods:
                food['_data_type'] = 'Foundation'
            all_foods.extend(foundation_foods)
            del data  # Free memory

        # Load SR Legacy Foods
        if files.get('sr_legacy'):
            data = load_json_file(files['sr_legacy'])
            sr_foods = data.get('SRLegacyFoods', [])
            print(f"[OK] Loaded {len(sr_foods)} SR Legacy foods")
            for food in sr_foods:
                food['_data_type'] = 'SR Legacy'
            all_foods.extend(sr_foods)
            del data  # Free memory

        # Load Survey/FNDDS Foods
        if files.get('survey'):
            data = load_json_file(files['survey'])
            survey_foods = data.get('SurveyFoods', [])
            print(f"[OK] Loaded {len(survey_foods)} Survey/FNDDS foods")
            for food in survey_foods:
                food['_data_type'] = 'Survey'
                # Survey foods use wweiaFoodCategory instead of foodCategory
                if 'wweiaFoodCategory' in food and 'foodCategory' not in food:
                    food['foodCategory'] = food['wweiaFoodCategory']
            all_foods.extend(survey_foods)
            del data  # Free memory

        # Import categories and nutrients from non-branded foods first
        if all_foods:
            import_categories(all_foods)
            import_nutrients(all_foods)

        # Import Foundation foods
        if files.get('foundation'):
            foundation_foods = [f for f in all_foods if f.get('_data_type') == 'Foundation']
            import_foods(foundation_foods, 'Foundation')

        # Import SR Legacy foods
        if files.get('sr_legacy'):
            sr_foods = [f for f in all_foods if f.get('_data_type') == 'SR Legacy']
            import_foods(sr_foods, 'SR Legacy')

        # Import Survey foods
        if files.get('survey'):
            survey_foods = [f for f in all_foods if f.get('_data_type') == 'Survey']
            import_foods(survey_foods, 'Survey')

        # Clear all_foods to free memory before loading branded
        all_foods = []

        # Load and import Branded Foods (handle separately due to large size)
        if files.get('branded'):
            print("\n[...] Loading Branded Foods (this may take a while)...")
            data = load_json_file(files['branded'])
            branded_foods = data.get('BrandedFoods', [])
            print(f"[OK] Loaded {len(branded_foods)} Branded foods")

            # Import categories and nutrients from branded foods
            import_categories(branded_foods)
            import_nutrients(branded_foods)

            # Mark data type and import
            for food in branded_foods:
                food['_data_type'] = 'Branded'
                # Branded foods use brandedFoodCategory
                if 'brandedFoodCategory' in food and 'foodCategory' not in food:
                    food['foodCategory'] = {'description': food['brandedFoodCategory']}

            import_foods(branded_foods, 'Branded')
            del data, branded_foods  # Free memory

        update_category_counts()
        print_summary()

        print("\n[OK] Import completed successfully!")


if __name__ == '__main__':
    main()
