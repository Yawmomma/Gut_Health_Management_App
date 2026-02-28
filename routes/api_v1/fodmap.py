"""
FODMAP Reference API v1 Endpoints
FODMAP category reference data and food filtering
"""

from flask import request, jsonify
from . import bp
from database import db
from models.food import Food
from sqlalchemy import func, or_
from utils.auth import require_api_key, require_scope


# =============================================================================
# ENDPOINTS
# =============================================================================

@bp.route('/fodmap/categories', methods=['GET'])
@require_api_key
@require_scope('read:fodmap')
def get_fodmap_categories():
    """
    Get distinct FODMAP food categories with counts

    Returns:
        JSON: Array of {name: str, count: int}

    Note:
        Only includes foods with at least one FODMAP rating set
        Excludes USDA-imported foods that have no FODMAP data
    """
    # Only include foods with at least one FODMAP rating set
    # (excludes USDA-imported foods that have no FODMAP data)
    fodmap_filter = or_(
        Food.fructans.isnot(None), Food.gos.isnot(None),
        Food.lactose.isnot(None), Food.fructose.isnot(None),
        Food.polyols.isnot(None), Food.mannitol.isnot(None),
        Food.sorbitol.isnot(None)
    )

    results = db.session.query(
        Food.category,
        func.count(Food.id).label('count')
    ).filter(fodmap_filter).group_by(Food.category).order_by(Food.category).all()

    return jsonify([
        {'name': cat, 'count': count}
        for cat, count in results if cat
    ])


@bp.route('/fodmap/foods', methods=['GET'])
@require_api_key
@require_scope('read:fodmap')
def get_fodmap_foods_by_category():
    """
    Get FODMAP foods in a specific category

    Query Parameters:
        category (str, required): Food category to filter by

    Returns:
        JSON: Array of {id: int, name: str, category: str}

    Error:
        400: Category parameter is required
        500: Server error
    """
    try:
        category = request.args.get('category', '')
        if not category:
            return jsonify({'error': 'Category parameter is required'}), 400

        foods = Food.query.filter(
            Food.usda_food_id.is_(None),
            Food.ausnut_food_id.is_(None),
            Food.category == category
        ).order_by(Food.name).all()
        return jsonify([
            {'id': f.id, 'name': f.name, 'category': f.category}
            for f in foods
        ])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
