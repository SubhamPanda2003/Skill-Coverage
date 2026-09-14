```python
class InvalidInputError(Exception):
    """Raise this error when a value cannot be converted to an integer."""


def safe_str_to_int(value):
    """Convert a string to an integer safely.

    Attempt to parse the given value as an integer. If the value
    cannot be converted, raise a custom InvalidInputError instead of
    letting the underlying ValueError or TypeError propagate.

    Args:
        value (str): The string to convert to an integer.

    Returns:
        int: The integer value parsed from the input string.

    Raises:
        InvalidInputError: If the value is None, not a string or
            integer, or cannot be parsed as a valid integer.
    """
    try:
        return int(value)
    except (ValueError, TypeError) as err:
        raise InvalidInputError(
            f"Cannot convert {value!r} to an integer"
        ) from err
```