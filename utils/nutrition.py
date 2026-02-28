"""
Shared nutrition calculation utilities
Used by both routes/diary.py and routes/api_v1/diary.py
"""

import re
import json


def _get_portion_multiplier(portion_size):
    if not portion_size:
        return None, None, None

    portion_lower = portion_size.lower().strip()
    number_match = re.search(r'(\d+\.?\d*)', portion_lower)

    if not number_match:
        return 1.0, True, 1.0

    num_value = float(number_match.group(1))
    if 'serv' in portion_lower:
        return num_value, True, num_value
    if 'g' in portion_lower and 'mg' not in portion_lower:
        return num_value / 100.0, False, None
    if 'ml' in portion_lower:
        return num_value / 100.0, False, None

    return num_value, True, num_value


def parse_portion_and_calculate_nutrition(portion_size, food):
    """
    Parse portion size string and calculate nutrition values.
    Returns dict with num_servings, energy_kj, protein_g, fat_g, carbs_g, sodium_mg

    Supported formats:
    - "2 servings", "1.5 serves", "1 serve" - multiply by per_serve values
    - "150g", "200 g" - calculate from per_100 values
    - "250ml", "300 ml" - calculate from per_100 values (treating ml as g)
    """
    result = {
        'num_servings': None,
        'energy_kj': None,
        'protein_g': None,
        'fat_g': None,
        'carbs_g': None,
        'sodium_mg': None
    }

    if not portion_size or not food:
        return result

    multiplier, use_per_serve, num_servings = _get_portion_multiplier(portion_size)
    if multiplier is None:
        return result

    result['num_servings'] = num_servings

    # Calculate nutrition based on multiplier
    if use_per_serve:
        # Use per_serve values
        if food.energy_per_serve_kj is not None:
            result['energy_kj'] = round(food.energy_per_serve_kj * multiplier, 1)
        if food.protein_per_serve is not None:
            result['protein_g'] = round(food.protein_per_serve * multiplier, 1)
        if food.fat_per_serve is not None:
            result['fat_g'] = round(food.fat_per_serve * multiplier, 1)
        if food.carbohydrate_per_serve is not None:
            result['carbs_g'] = round(food.carbohydrate_per_serve * multiplier, 1)
        if food.sodium_per_serve is not None:
            result['sodium_mg'] = round(food.sodium_per_serve * multiplier, 1)
    else:
        # Use per_100 values
        if food.energy_per_100_kj is not None:
            result['energy_kj'] = round(food.energy_per_100_kj * multiplier, 1)
        if food.protein_per_100 is not None:
            result['protein_g'] = round(food.protein_per_100 * multiplier, 1)
        if food.fat_per_100 is not None:
            result['fat_g'] = round(food.fat_per_100 * multiplier, 1)
        if food.carbohydrate_per_100 is not None:
            result['carbs_g'] = round(food.carbohydrate_per_100 * multiplier, 1)
        if food.sodium_per_100 is not None:
            result['sodium_mg'] = round(food.sodium_per_100 * multiplier, 1)

    return result


def calculate_nutrition_breakdown(portion_size, food, num_servings=None):
    if not food:
        return {}

    if not portion_size and num_servings is not None:
        portion_size = f"{num_servings} servings"

    multiplier, use_per_serve, _ = _get_portion_multiplier(portion_size)
    if multiplier is None:
        return {}

    def scale(value):
        if value is None:
            return None
        return round(value * multiplier, 2)

    def choose(per_serve, per_100):
        return per_serve if use_per_serve else per_100

    details = {
        'energy_kj': scale(choose(food.energy_per_serve_kj, food.energy_per_100_kj)),
        'energy_cal': scale(choose(food.energy_per_serve_cal, food.energy_per_100_cal)),
        'protein_g': scale(choose(food.protein_per_serve, food.protein_per_100)),
        'fat_g': scale(choose(food.fat_per_serve, food.fat_per_100)),
        'sat_fat_g': scale(choose(food.saturated_fat_per_serve, food.saturated_fat_per_100)),
        'trans_fat_g': scale(choose(food.trans_fat_per_serve, food.trans_fat_per_100)),
        'poly_fat_g': scale(choose(food.polyunsaturated_fat_per_serve, food.polyunsaturated_fat_per_100)),
        'mono_fat_g': scale(choose(food.monounsaturated_fat_per_serve, food.monounsaturated_fat_per_100)),
        'carbs_g': scale(choose(food.carbohydrate_per_serve, food.carbohydrate_per_100)),
        'sugars_g': scale(choose(food.sugars_per_serve, food.sugars_per_100)),
        'lactose_g': scale(choose(food.lactose_per_serve, food.lactose_per_100)),
        'galactose_g': scale(choose(food.galactose_per_serve, food.galactose_per_100)),
        'fibre_g': scale(choose(food.dietary_fibre_per_serve, food.dietary_fibre_per_100)),
        'cholesterol_mg': scale(choose(food.cholesterol_per_serve, food.cholesterol_per_100)),
        'sodium_mg': scale(choose(food.sodium_per_serve, food.sodium_per_100)),
        'potassium_mg': scale(choose(food.potassium_per_serve, food.potassium_per_100)),
        'calcium_mg': scale(choose(food.calcium_per_serve, food.calcium_per_100)),
        'phosphorus_mg': scale(choose(food.phosphorus_per_serve, food.phosphorus_per_100)),
        'vitamin_a': scale(choose(food.vitamin_a_per_serve, food.vitamin_a_per_100)),
        'vitamin_b12': scale(choose(food.vitamin_b12_per_serve, food.vitamin_b12_per_100)),
        'vitamin_d': scale(choose(food.vitamin_d_per_serve, food.vitamin_d_per_100)),
        'riboflavin_b2': scale(choose(food.riboflavin_b2_per_serve, food.riboflavin_b2_per_100)),
        'vitamin_a_unit': food.vitamin_a_unit or 'mcg',
        'vitamin_b12_unit': food.vitamin_b12_unit or 'mcg',
        'vitamin_d_unit': food.vitamin_d_unit or 'mcg',
        'riboflavin_b2_unit': food.riboflavin_b2_unit or 'mg',
        'custom_nutrients': {
            'vitamins': [],
            'minerals': [],
            'macros': []
        }
    }

    if food.custom_nutrients:
        try:
            custom = json.loads(food.custom_nutrients)
            for group in ['vitamins', 'minerals', 'macros']:
                for item in custom.get(group, []):
                    base_value = item.get('per_serve') if use_per_serve else item.get('per_100')
                    if base_value is None:
                        continue
                    details['custom_nutrients'][group].append({
                        'name': item.get('name', 'Custom'),
                        'value': scale(base_value),
                        'unit': item.get('unit', '')
                    })
        except Exception:
            pass

    return details
