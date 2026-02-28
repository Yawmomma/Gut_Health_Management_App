"""
Input validation utilities for API endpoints
Provides consistent validation with clear error messages
"""

from datetime import datetime
from typing import List, Any, Optional


class ValidationError(ValueError):
    """Custom exception for validation errors"""
    pass


def validate_date_string(date_str: Any, field_name: str = 'date') -> str:
    """
    Validate YYYY-MM-DD date format

    Args:
        date_str: Date string to validate
        field_name: Name of the field for error messages

    Returns:
        str: Validated date string

    Raises:
        ValidationError: If date format is invalid
    """
    if not date_str:
        raise ValidationError(f'{field_name} is required')

    if not isinstance(date_str, str):
        raise ValidationError(f'{field_name} must be a string')

    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        raise ValidationError(f'{field_name} must be in YYYY-MM-DD format (e.g., 2026-02-13)')


def validate_positive_int(value: Any, field_name: str = 'value',
                         min_val: int = 1, max_val: Optional[int] = None) -> int:
    """
    Validate positive integer with optional range

    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        min_val: Minimum allowed value (default: 1)
        max_val: Maximum allowed value (default: None = unlimited)

    Returns:
        int: Validated integer value

    Raises:
        ValidationError: If value is not a valid integer or out of range
    """
    if value is None:
        raise ValidationError(f'{field_name} is required')

    try:
        int_val = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f'{field_name} must be a valid integer')

    if int_val < min_val:
        raise ValidationError(f'{field_name} must be at least {min_val}')

    if max_val is not None and int_val > max_val:
        raise ValidationError(f'{field_name} must be at most {max_val}')

    return int_val


def validate_optional_int(value: Any, field_name: str = 'value',
                         min_val: Optional[int] = None,
                         max_val: Optional[int] = None,
                         default: Optional[int] = None) -> Optional[int]:
    """
    Validate optional integer with range

    Args:
        value: Value to validate (can be None)
        field_name: Name of the field for error messages
        min_val: Minimum allowed value (default: None = no minimum)
        max_val: Maximum allowed value (default: None = no maximum)
        default: Default value if None (default: None)

    Returns:
        int or None: Validated integer value or default

    Raises:
        ValidationError: If value is not a valid integer or out of range
    """
    if value is None or value == '':
        return default

    try:
        int_val = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f'{field_name} must be a valid integer')

    if min_val is not None and int_val < min_val:
        raise ValidationError(f'{field_name} must be at least {min_val}')

    if max_val is not None and int_val > max_val:
        raise ValidationError(f'{field_name} must be at most {max_val}')

    return int_val


def validate_enum(value: Any, allowed_values: List[str],
                 field_name: str = 'value',
                 case_sensitive: bool = False) -> str:
    """
    Validate value is in allowed list

    Args:
        value: Value to validate
        allowed_values: List of allowed values
        field_name: Name of the field for error messages
        case_sensitive: Whether comparison should be case-sensitive

    Returns:
        str: Validated value

    Raises:
        ValidationError: If value is not in allowed list
    """
    if not value:
        raise ValidationError(f'{field_name} is required')

    if not isinstance(value, str):
        raise ValidationError(f'{field_name} must be a string')

    # Normalize for comparison
    if case_sensitive:
        if value not in allowed_values:
            raise ValidationError(
                f'{field_name} must be one of: {", ".join(allowed_values)}'
            )
    else:
        value_lower = value.lower()
        allowed_lower = [v.lower() for v in allowed_values]
        if value_lower not in allowed_lower:
            raise ValidationError(
                f'{field_name} must be one of: {", ".join(allowed_values)}'
            )

    return value


def validate_optional_enum(value: Any, allowed_values: List[str],
                          field_name: str = 'value',
                          case_sensitive: bool = False,
                          default: Optional[str] = None) -> Optional[str]:
    """
    Validate optional enum value

    Args:
        value: Value to validate (can be None)
        allowed_values: List of allowed values
        field_name: Name of the field for error messages
        case_sensitive: Whether comparison should be case-sensitive
        default: Default value if None

    Returns:
        str or None: Validated value or default

    Raises:
        ValidationError: If value is not in allowed list
    """
    if not value or value == '':
        return default

    return validate_enum(value, allowed_values, field_name, case_sensitive)


def validate_array_size(arr: Any, field_name: str = 'items',
                       min_size: int = 0, max_size: int = 100) -> List:
    """
    Validate array/list size

    Args:
        arr: Array to validate
        field_name: Name of the field for error messages
        min_size: Minimum number of items (default: 0)
        max_size: Maximum number of items (default: 100)

    Returns:
        list: Validated array

    Raises:
        ValidationError: If array size is out of range
    """
    if not isinstance(arr, (list, tuple)):
        raise ValidationError(f'{field_name} must be an array')

    size = len(arr)

    if size < min_size:
        raise ValidationError(f'{field_name} must contain at least {min_size} items')

    if size > max_size:
        raise ValidationError(f'{field_name} must contain at most {max_size} items')

    return list(arr)


def validate_string_length(value: Any, field_name: str = 'value',
                          min_length: int = 0, max_length: int = 1000,
                          required: bool = True) -> Optional[str]:
    """
    Validate string length

    Args:
        value: String to validate
        field_name: Name of the field for error messages
        min_length: Minimum string length (default: 0)
        max_length: Maximum string length (default: 1000)
        required: Whether the field is required (default: True)

    Returns:
        str or None: Validated string

    Raises:
        ValidationError: If string length is out of range
    """
    if value is None or value == '':
        if required:
            raise ValidationError(f'{field_name} is required')
        return None

    if not isinstance(value, str):
        raise ValidationError(f'{field_name} must be a string')

    length = len(value)

    if length < min_length:
        raise ValidationError(f'{field_name} must be at least {min_length} characters')

    if length > max_length:
        raise ValidationError(f'{field_name} must be at most {max_length} characters')

    return value


def validate_year_month(year: Any, month: Any) -> tuple:
    """
    Validate year and month values

    Args:
        year: Year value to validate
        month: Month value to validate

    Returns:
        tuple: (validated_year, validated_month)

    Raises:
        ValidationError: If year or month is invalid
    """
    try:
        year_int = int(year)
        month_int = int(month)
    except (ValueError, TypeError):
        raise ValidationError('Year and month must be valid integers')

    if year_int < 2000 or year_int > 2100:
        raise ValidationError('Year must be between 2000 and 2100')

    if month_int < 1 or month_int > 12:
        raise ValidationError('Month must be between 1 and 12')

    return year_int, month_int


def validate_date_range(start_date: Any, end_date: Any) -> tuple:
    """
    Validate date range (start must be before or equal to end)

    Args:
        start_date: Start date string (YYYY-MM-DD)
        end_date: End date string (YYYY-MM-DD)

    Returns:
        tuple: (validated_start_date, validated_end_date)

    Raises:
        ValidationError: If dates are invalid or end is before start
    """
    start = validate_date_string(start_date, 'start_date')
    end = validate_date_string(end_date, 'end_date')

    start_dt = datetime.strptime(start, '%Y-%m-%d')
    end_dt = datetime.strptime(end, '%Y-%m-%d')

    if end_dt < start_dt:
        raise ValidationError('end_date must be on or after start_date')

    return start, end


# Common enum values for validation
MEAL_TYPES = ['Breakfast', 'Lunch', 'Dinner', 'Snack', 'Other']
SERVING_TYPES = ['safe', 'moderate', 'high']
SEVERITY_LEVELS = ['Mild', 'Moderate', 'Severe', 'Extreme']
STOOL_TYPES = ['Type 1', 'Type 2', 'Type 3', 'Type 4', 'Type 5', 'Type 6', 'Type 7']
STRESS_LEVELS = ['Low', 'Medium', 'High']
RECIPE_CATEGORIES = ['Breakfast', 'Lunch', 'Dinner', 'Snacks', 'Desserts', 'Beverages', 'Salads', 'Sauces & Gravies', 'Other']
DIFFICULTY_LEVELS = ['Quick & Easy', 'Under 15 Minutes', 'Under 30 Minutes', 'Beginner-Friendly', 'Intermediate', 'Advanced']
