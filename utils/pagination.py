"""
Pagination utilities for API endpoints
Provides consistent pagination across all list endpoints
"""

from typing import Dict, List, Any, Optional
from utils.validators import validate_optional_int, ValidationError


def paginate_query(query, page: int = 1, per_page: int = 50, max_per_page: int = 100) -> Dict[str, Any]:
    """
    Helper function for consistent pagination using Flask-SQLAlchemy

    Args:
        query: SQLAlchemy query object to paginate
        page: Page number (1-indexed, default: 1)
        per_page: Items per page (default: 50)
        max_per_page: Maximum items per page (default: 100)

    Returns:
        dict: Paginated response with data and pagination metadata
        {
            "data": [...],
            "pagination": {
                "page": 1,
                "per_page": 50,
                "total": 1247,
                "pages": 25,
                "has_next": true,
                "has_prev": false
            }
        }

    Example:
        from models.food import Food
        query = Food.query.filter_by(category='Fruit')
        return jsonify(paginate_query(query, page=1, per_page=20))
    """
    # Limit per_page to max_per_page
    per_page = min(per_page, max_per_page)

    # Execute pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # Return paginated data with metadata
    return {
        'data': [item.to_dict() for item in pagination.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }


def paginate_list(items: List[Any], page: int = 1, per_page: int = 50, max_per_page: int = 100) -> Dict[str, Any]:
    """
    Helper function for paginating a list of items (already in memory)

    Args:
        items: List of items to paginate
        page: Page number (1-indexed, default: 1)
        per_page: Items per page (default: 50)
        max_per_page: Maximum items per page (default: 100)

    Returns:
        dict: Paginated response with data and pagination metadata

    Example:
        foods = [food1, food2, food3, ...]
        return jsonify(paginate_list(foods, page=1, per_page=20))
    """
    # Limit per_page to max_per_page
    per_page = min(per_page, max_per_page)

    # Calculate pagination
    total = len(items)
    pages = (total + per_page - 1) // per_page  # Ceiling division

    # Ensure page is within bounds
    page = max(1, min(page, max(pages, 1)))

    # Calculate slice indices
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    # Slice data
    page_items = items[start_idx:end_idx]

    return {
        'data': page_items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': pages,
            'has_next': page < pages,
            'has_prev': page > 1
        }
    }


def get_pagination_params(request_args: Dict[str, Any],
                         default_page: int = 1,
                         default_per_page: int = 50,
                         max_per_page: int = 100) -> tuple:
    """
    Extract and validate pagination parameters from request args

    Args:
        request_args: Request arguments (usually request.args)
        default_page: Default page number (default: 1)
        default_per_page: Default items per page (default: 50)
        max_per_page: Maximum items per page (default: 100)

    Returns:
        tuple: (page, per_page) validated integers

    Raises:
        ValidationError: If parameters are invalid

    Example:
        from flask import request
        try:
            page, per_page = get_pagination_params(request.args)
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400
    """
    # Validate page parameter
    page = validate_optional_int(
        request_args.get('page'),
        field_name='page',
        min_val=1,
        default=default_page
    )

    # Validate per_page parameter
    per_page = validate_optional_int(
        request_args.get('per_page'),
        field_name='per_page',
        min_val=1,
        max_val=max_per_page,
        default=default_per_page
    )

    return page, per_page
