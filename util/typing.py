# Imports
from typing import get_args, get_origin, Any, Type


def is_valid_type(value: Any, expected_type: Type) -> bool:
    """
    Check if the value is of the expected type, including handling generic
    types

    Args:
        value (Any): The value to check the type of.
        expected_type (Type): The expected type. Can be a regular type or a
            generic type from the typing module.

    Returns:
        bool: True if value is of the expected type, False otherwise.
    """

    # Check if the origin is nonexistent
    if get_origin(expected_type) is not None:
        # Handle generic types (e.g., List, Dict)
        if isinstance(value, get_origin(expected_type)):
            # Check if each element in the list/dict matches the inner type
            inner_types = get_args(expected_type)
            if inner_types:
                return all(
                    is_valid_type(item, inner_types[0]) for item in value
                )
            return True
        return False

    # If not, check instance normally
    else:
        # Handle non-generic types
        return isinstance(value, expected_type)
