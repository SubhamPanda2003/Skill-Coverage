```python
class InvalidInputError(Exception):
    """Exception raised when a value cannot be converted to an integer."""


def string_to_int(value):
    """Convert a string to an integer safely.

    Args:
        value: The string to convert to an integer.

    Returns:
        The integer value parsed from the given string.

    Raises:
        InvalidInputError: If the value cannot be converted to an
            integer.
    """
    try:
        return int(value)
    except (ValueError, TypeError) as err:
        raise InvalidInputError(
            f"Cannot convert {value!r} to an integer"
        ) from err
```