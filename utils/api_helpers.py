"""
API Response Helpers
Provides standardized response formats for success and error responses
"""

from flask import jsonify
from typing import Any, Optional, Dict


# ============================================================================
# ERROR CODES
# ============================================================================

# Client Errors (4xx)
VALIDATION_ERROR = 'VALIDATION_ERROR'
NOT_FOUND = 'NOT_FOUND'
ALREADY_EXISTS = 'ALREADY_EXISTS'
INVALID_CREDENTIALS = 'INVALID_CREDENTIALS'
MISSING_REQUIRED_FIELD = 'MISSING_REQUIRED_FIELD'
INVALID_FORMAT = 'INVALID_FORMAT'
OUT_OF_RANGE = 'OUT_OF_RANGE'
FORBIDDEN = 'FORBIDDEN'
UNAUTHORIZED = 'UNAUTHORIZED'

# Server Errors (5xx)
DATABASE_ERROR = 'DATABASE_ERROR'
EXTERNAL_SERVICE_ERROR = 'EXTERNAL_SERVICE_ERROR'
INTERNAL_SERVER_ERROR = 'INTERNAL_SERVER_ERROR'
NOT_IMPLEMENTED = 'NOT_IMPLEMENTED'

# Mapping of error codes to HTTP status codes
ERROR_STATUS_MAP = {
    # 400 Bad Request
    VALIDATION_ERROR: 400,
    MISSING_REQUIRED_FIELD: 400,
    INVALID_FORMAT: 400,
    OUT_OF_RANGE: 400,

    # 401 Unauthorized
    UNAUTHORIZED: 401,
    INVALID_CREDENTIALS: 401,

    # 403 Forbidden
    FORBIDDEN: 403,

    # 404 Not Found
    NOT_FOUND: 404,

    # 409 Conflict
    ALREADY_EXISTS: 409,

    # 500 Internal Server Error
    DATABASE_ERROR: 500,
    EXTERNAL_SERVICE_ERROR: 500,
    INTERNAL_SERVER_ERROR: 500,

    # 501 Not Implemented
    NOT_IMPLEMENTED: 501
}


# ============================================================================
# RESPONSE FUNCTIONS
# ============================================================================

def error_response(message: str,
                  code: str = INTERNAL_SERVER_ERROR,
                  status: Optional[int] = None,
                  details: Optional[Dict[str, Any]] = None):
    """
    Standardized error response

    Args:
        message: Human-readable error message
        code: Error code from predefined constants (default: INTERNAL_SERVER_ERROR)
        status: HTTP status code (default: auto-determined from code)
        details: Additional error details (optional)

    Returns:
        tuple: (flask.Response, status_code)

    Example:
        return error_response('Food not found', code=NOT_FOUND)
        return error_response('Invalid date', code=VALIDATION_ERROR, details={'field': 'date'})
    """
    # Determine status code
    if status is None:
        status = ERROR_STATUS_MAP.get(code, 500)

    # Build response
    response = {
        'success': False,
        'error': {
            'code': code,
            'message': message
        }
    }

    # Add details if provided
    if details:
        response['error']['details'] = details

    return jsonify(response), status


def success_response(data: Any,
                    message: Optional[str] = None,
                    status: int = 200):
    """
    Standardized success response

    Args:
        data: Response data (can be dict, list, or any JSON-serializable type)
        message: Optional success message
        status: HTTP status code (default: 200)

    Returns:
        tuple: (flask.Response, status_code)

    Example:
        return success_response({'id': 123, 'name': 'Apple'})
        return success_response([], message='No results found')
        return success_response({'id': 456}, message='Food created', status=201)
    """
    response = {
        'success': True,
        'data': data
    }

    # Add message if provided
    if message:
        response['message'] = message

    return jsonify(response), status


def validation_error(message: str, field: Optional[str] = None):
    """
    Shorthand for validation error response

    Args:
        message: Error message
        field: Field name that failed validation (optional)

    Returns:
        tuple: (flask.Response, 400)

    Example:
        return validation_error('Date must be in YYYY-MM-DD format', field='date')
    """
    details = {'field': field} if field else None
    return error_response(message, code=VALIDATION_ERROR, details=details)


def not_found_error(resource: str, identifier: Any = None):
    """
    Shorthand for not found error response

    Args:
        resource: Name of the resource (e.g., 'Food', 'Recipe')
        identifier: Resource identifier (optional)

    Returns:
        tuple: (flask.Response, 404)

    Example:
        return not_found_error('Food', 123)
        return not_found_error('Recipe')
    """
    if identifier is not None:
        message = f'{resource} with ID {identifier} not found'
    else:
        message = f'{resource} not found'

    return error_response(message, code=NOT_FOUND)


def database_error(message: str = 'Database operation failed'):
    """
    Shorthand for database error response

    Args:
        message: Error message (optional)

    Returns:
        tuple: (flask.Response, 500)

    Example:
        return database_error('Failed to save food entry')
    """
    return error_response(message, code=DATABASE_ERROR)


def already_exists_error(resource: str, identifier: Optional[str] = None):
    """
    Shorthand for resource already exists error

    Args:
        resource: Name of the resource
        identifier: Resource identifier (optional)

    Returns:
        tuple: (flask.Response, 409)

    Example:
        return already_exists_error('Food', 'Apple (Fuji)')
        return already_exists_error('User email')
    """
    if identifier:
        message = f'{resource} "{identifier}" already exists'
    else:
        message = f'{resource} already exists'

    return error_response(message, code=ALREADY_EXISTS)


def missing_field_error(field: str):
    """
    Shorthand for missing required field error

    Args:
        field: Name of the missing field

    Returns:
        tuple: (flask.Response, 400)

    Example:
        return missing_field_error('recipe_name')
    """
    return error_response(
        f'{field} is required',
        code=MISSING_REQUIRED_FIELD,
        details={'field': field}
    )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def paginated_response(data: list,
                      page: int,
                      per_page: int,
                      total: int,
                      message: Optional[str] = None):
    """
    Standardized paginated response

    Args:
        data: List of items for current page
        page: Current page number
        per_page: Items per page
        total: Total number of items
        message: Optional message

    Returns:
        tuple: (flask.Response, 200)

    Example:
        return paginated_response(
            data=foods,
            page=1,
            per_page=50,
            total=1247,
            message='Foods retrieved successfully'
        )
    """
    pages = (total + per_page - 1) // per_page

    response_data = {
        'data': data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': pages,
            'has_next': page < pages,
            'has_prev': page > 1
        }
    }

    return success_response(response_data, message=message)


def wrap_exception(e: Exception, default_code: str = INTERNAL_SERVER_ERROR):
    """
    Wrap an exception into a standardized error response

    Args:
        e: Exception object
        default_code: Default error code if not a known exception type

    Returns:
        tuple: (flask.Response, status_code)

    Example:
        try:
            # database operation
        except Exception as e:
            return wrap_exception(e)
    """
    # Handle validation errors
    from utils.validators import ValidationError
    if isinstance(e, ValidationError):
        return error_response(str(e), code=VALIDATION_ERROR)

    # Handle database errors
    from sqlalchemy.exc import IntegrityError, OperationalError
    if isinstance(e, IntegrityError):
        return error_response('Database integrity constraint violated', code=DATABASE_ERROR)
    if isinstance(e, OperationalError):
        return error_response('Database operation failed', code=DATABASE_ERROR)

    # Default: internal server error
    return error_response(str(e), code=default_code)


# ============================================================================
# WEBHOOK SIGNATURE VERIFICATION
# ============================================================================

def verify_webhook_signature(payload_body, signature_header, secret, algorithm='sha256'):
    """
    Verify HMAC signature for incoming webhook payloads.

    Args:
        payload_body: Raw request body bytes
        signature_header: The signature from the request header (e.g., 'sha256=abc123...')
        secret: The shared secret key
        algorithm: Hash algorithm (default: sha256)

    Returns:
        True if signature is valid, False if invalid, None if no secret configured (skip)
    """
    if not secret:
        return None  # No secret configured, skip validation

    if not signature_header:
        return False  # Secret configured but no signature provided

    import hmac
    import hashlib

    # Handle 'sha256=hexdigest' format (Stripe/GitHub style)
    if '=' in signature_header:
        parts = signature_header.split('=', 1)
        expected_sig = parts[1]
    else:
        expected_sig = signature_header

    hash_func = getattr(hashlib, algorithm, hashlib.sha256)
    computed = hmac.new(
        secret.encode('utf-8'),
        payload_body,
        hash_func
    ).hexdigest()

    return hmac.compare_digest(computed, expected_sig)
