"""
Recipe Parser Utility
Parses raw recipe text from external datasets into structured data.
"""
import re
import hashlib
from typing import Optional


def generate_recipe_hash(text: str) -> str:
    """Generate a unique hash for a recipe based on its content."""
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def parse_recipe_text(text: str) -> dict:
    """
    Parse recipe text from the all-recipes dataset format.

    Expected format:
    "Recipe Name Ingredients: - item1 - item2 ... Directions: - step1 - step2 ..."

    Returns:
        dict with keys: name, ingredients (list), directions (list), servings, raw_text, hash
    """
    if not text or not isinstance(text, str):
        return {
            'name': 'Unknown Recipe',
            'ingredients': [],
            'directions': [],
            'servings': None,
            'raw_text': text or '',
            'hash': generate_recipe_hash(text or '')
        }

    result = {
        'name': '',
        'ingredients': [],
        'directions': [],
        'servings': None,
        'raw_text': text,
        'hash': generate_recipe_hash(text)
    }

    # Try to find "Ingredients:" marker
    ingredients_match = re.search(r'(.+?)\s*Ingredients:', text, re.IGNORECASE)
    if ingredients_match:
        result['name'] = ingredients_match.group(1).strip()
    else:
        # Fallback: first line or first few words
        lines = text.split('\n')
        if lines:
            first_line = lines[0].strip()
            # Take up to first 50 chars or until we hit a common marker
            result['name'] = first_line[:100] if len(first_line) <= 100 else first_line[:100] + '...'

    # Extract ingredients section
    ingredients_section = re.search(
        r'Ingredients:\s*(.*?)(?:Directions:|Instructions:|$)',
        text,
        re.IGNORECASE | re.DOTALL
    )
    if ingredients_section:
        ingredients_text = ingredients_section.group(1)
        # Split by " - " pattern (typical format)
        raw_ingredients = re.split(r'\s*-\s+', ingredients_text)
        result['ingredients'] = [
            ing.strip() for ing in raw_ingredients
            if ing.strip() and len(ing.strip()) > 1
        ]

    # Extract directions section
    directions_section = re.search(
        r'(?:Directions|Instructions):\s*(.*?)$',
        text,
        re.IGNORECASE | re.DOTALL
    )
    if directions_section:
        directions_text = directions_section.group(1)
        # Split by " - " pattern or numbered steps
        raw_directions = re.split(r'\s*-\s+|\s*\d+\.\s+', directions_text)
        result['directions'] = [
            step.strip() for step in raw_directions
            if step.strip() and len(step.strip()) > 1
        ]

    # Try to extract servings info
    servings_match = re.search(
        r'(?:Yields?|Serves?|Makes?)\s*:?\s*(\d+)',
        text,
        re.IGNORECASE
    )
    if servings_match:
        try:
            result['servings'] = int(servings_match.group(1))
        except ValueError:
            pass

    return result


def format_ingredients_for_display(ingredients: list) -> str:
    """Format ingredients list for display with bullet points."""
    if not ingredients:
        return "No ingredients listed"
    return '\n'.join(f"• {ing}" for ing in ingredients)


def format_directions_for_display(directions: list) -> str:
    """Format directions list for display with numbered steps."""
    if not directions:
        return "No directions listed"
    return '\n'.join(f"{i+1}. {step}" for i, step in enumerate(directions))


def extract_ingredient_names(ingredients: list) -> list:
    """
    Extract just the food names from ingredient strings (removing quantities).
    Useful for matching against the food library.

    Example: "1 c. brown sugar" -> "brown sugar"
    """
    cleaned = []
    for ing in ingredients:
        # Remove common quantity patterns
        # Pattern: number + unit + ingredient
        clean = re.sub(
            r'^[\d\s/½¼¾⅓⅔⅛]+\s*'  # Numbers and fractions
            r'(?:c\.|cup|cups|tsp\.|teaspoon|teaspoons|tbsp\.|tablespoon|tablespoons|'
            r'oz\.|ounce|ounces|lb\.|pound|pounds|pkg\.|package|packages|'
            r'can|cans|jar|jars|bunch|bunches|head|heads|clove|cloves|'
            r'slice|slices|piece|pieces|stick|sticks|small|medium|large|'
            r'pinch|dash|to taste)s?\s*',
            '',
            ing,
            flags=re.IGNORECASE
        )
        # Remove parenthetical notes
        clean = re.sub(r'\([^)]*\)', '', clean)
        # Clean up extra whitespace
        clean = ' '.join(clean.split()).strip()
        if clean:
            cleaned.append(clean.lower())
    return cleaned


def search_text_contains_all(text: str, search_terms: list) -> bool:
    """Check if text contains all search terms (case-insensitive)."""
    text_lower = text.lower()
    return all(term.lower() in text_lower for term in search_terms)


def search_text_contains_any(text: str, search_terms: list) -> bool:
    """Check if text contains any of the search terms (case-insensitive)."""
    text_lower = text.lower()
    return any(term.lower() in text_lower for term in search_terms)
