```python
"""Utilities for safely converting strings to integers."""


class InvalidInputError(Exception):
    """Signal that a value cannot be converted to an integer."""


def safe_string_to_int(value):
    """Convert a string to an integer safely.

    Args:
        value: The string to convert to an integer.

    Returns:
        The integer value represented by the string.

    Raises:
        InvalidInputError: If the value is not a string or
            cannot be parsed as an integer.
    """
    if not isinstance(value, str):
        type_name = type(value).__name__
        raise InvalidInputError(
            f'Expected a string, got {type_name}.'
        )

    try:
        return int(value.strip())
    except ValueError as err:
        raise InvalidInputError(
            f'Cannot convert {value!r} to an integer.'
        ) from err
```