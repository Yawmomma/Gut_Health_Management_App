"""
Recipe Search Utility
Polars-based search engine for external recipe parquet files.
"""
import os
from pathlib import Path
from typing import Optional
import polars as pl
from utils.recipe_parser import parse_recipe_text, generate_recipe_hash


# Path to parquet files
RECIPE_DATA_DIR = Path(__file__).parent.parent / 'data' / 'recipes' / 'external'

# Cache for lazy frame (avoids re-reading files each search)
_recipe_lazy_frame = None
_total_recipes = None


def get_parquet_files() -> list:
    """Get list of all parquet files in the data directory."""
    if not RECIPE_DATA_DIR.exists():
        return []
    return list(RECIPE_DATA_DIR.glob('*.parquet'))


def get_recipe_lazy_frame() -> Optional[pl.LazyFrame]:
    """
    Get a lazy frame for all recipe parquet files.
    Uses caching to avoid re-reading files.
    """
    global _recipe_lazy_frame

    if _recipe_lazy_frame is not None:
        return _recipe_lazy_frame

    parquet_files = get_parquet_files()
    if not parquet_files:
        return None

    # Create lazy frame from all parquet files
    _recipe_lazy_frame = pl.scan_parquet(parquet_files)
    return _recipe_lazy_frame


def get_total_recipe_count() -> int:
    """Get total number of recipes in the dataset."""
    global _total_recipes

    if _total_recipes is not None:
        return _total_recipes

    lf = get_recipe_lazy_frame()
    if lf is None:
        return 0

    try:
        _total_recipes = lf.select(pl.len()).collect().item()
        return _total_recipes
    except Exception:
        return 0


def search_recipes(
    query: str,
    limit: int = 50,
    offset: int = 0,
    archived_hashes: set = None
) -> list:
    """
    Search recipes by keyword(s).

    Args:
        query: Search string (can contain multiple words)
        limit: Maximum number of results to return
        offset: Number of results to skip (for pagination)
        archived_hashes: Set of recipe hashes to exclude (archived recipes)

    Returns:
        List of dicts with parsed recipe data
    """
    lf = get_recipe_lazy_frame()
    if lf is None:
        return []

    if not query or not query.strip():
        return []

    # Split query into terms for AND search
    terms = [t.strip() for t in query.split() if t.strip()]
    if not terms:
        return []

    try:
        # Build filter for all terms (AND logic)
        filter_expr = pl.lit(True)
        for term in terms:
            filter_expr = filter_expr & pl.col('input').str.contains(f'(?i){term}')

        # Execute query with lazy evaluation
        results = (
            lf.filter(filter_expr)
            .slice(offset, limit + 100)  # Get extra to filter archived
            .collect()
        )

        # Parse results and filter archived
        parsed_results = []
        for row in results.iter_rows(named=True):
            raw_text = row.get('input', '')
            parsed = parse_recipe_text(raw_text)

            # Skip archived recipes
            if archived_hashes and parsed['hash'] in archived_hashes:
                continue

            parsed_results.append(parsed)
            if len(parsed_results) >= limit:
                break

        return parsed_results

    except Exception as e:
        print(f"Recipe search error: {e}")
        return []


def search_by_ingredients(
    ingredients: list,
    match_all: bool = True,
    limit: int = 50,
    archived_hashes: set = None
) -> list:
    """
    Search recipes that contain specified ingredients.

    Args:
        ingredients: List of ingredient names to search for
        match_all: If True, recipe must contain ALL ingredients; if False, ANY ingredient
        limit: Maximum number of results
        archived_hashes: Set of recipe hashes to exclude

    Returns:
        List of parsed recipe dicts
    """
    lf = get_recipe_lazy_frame()
    if lf is None or not ingredients:
        return []

    try:
        if match_all:
            # AND logic - must contain all ingredients
            filter_expr = pl.lit(True)
            for ing in ingredients:
                filter_expr = filter_expr & pl.col('input').str.contains(f'(?i){ing}')
        else:
            # OR logic - must contain at least one ingredient
            filter_expr = pl.lit(False)
            for ing in ingredients:
                filter_expr = filter_expr | pl.col('input').str.contains(f'(?i){ing}')

        results = (
            lf.filter(filter_expr)
            .head(limit + 50)
            .collect()
        )

        parsed_results = []
        for row in results.iter_rows(named=True):
            raw_text = row.get('input', '')
            parsed = parse_recipe_text(raw_text)

            if archived_hashes and parsed['hash'] in archived_hashes:
                continue

            parsed_results.append(parsed)
            if len(parsed_results) >= limit:
                break

        return parsed_results

    except Exception as e:
        print(f"Ingredient search error: {e}")
        return []


def get_random_recipes(limit: int = 10, archived_hashes: set = None) -> list:
    """
    Get random recipes for inspiration.

    Args:
        limit: Number of random recipes to return
        archived_hashes: Set of recipe hashes to exclude

    Returns:
        List of parsed recipe dicts
    """
    lf = get_recipe_lazy_frame()
    if lf is None:
        return []

    try:
        # Sample random rows
        results = (
            lf.collect()
            .sample(n=min(limit + 20, 100), shuffle=True)
            .head(limit + 20)
        )

        parsed_results = []
        for row in results.iter_rows(named=True):
            raw_text = row.get('input', '')
            parsed = parse_recipe_text(raw_text)

            if archived_hashes and parsed['hash'] in archived_hashes:
                continue

            parsed_results.append(parsed)
            if len(parsed_results) >= limit:
                break

        return parsed_results

    except Exception as e:
        print(f"Random recipes error: {e}")
        return []


def get_recipe_by_hash(recipe_hash: str) -> Optional[dict]:
    """
    Retrieve a specific recipe by its hash.
    This requires scanning all files which can be slow.

    Args:
        recipe_hash: MD5 hash of the recipe text

    Returns:
        Parsed recipe dict or None if not found
    """
    lf = get_recipe_lazy_frame()
    if lf is None:
        return None

    try:
        # We need to compute hash for each recipe to find match
        # This is expensive, so we do it in batches
        batch_size = 10000
        offset = 0

        while True:
            batch = lf.slice(offset, batch_size).collect()
            if len(batch) == 0:
                break

            for row in batch.iter_rows(named=True):
                raw_text = row.get('input', '')
                if generate_recipe_hash(raw_text) == recipe_hash:
                    return parse_recipe_text(raw_text)

            offset += batch_size

        return None

    except Exception as e:
        print(f"Get recipe by hash error: {e}")
        return None


def clear_cache():
    """Clear the cached lazy frame (useful if files change)."""
    global _recipe_lazy_frame, _total_recipes
    _recipe_lazy_frame = None
    _total_recipes = None
