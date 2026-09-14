```python
class InvalidInputError(Exception):
    """Raised when a value cannot be converted to an integer."""


def str_to_int(value):
    """Convert a string to an integer safely.

    Args:
        value: The string to convert to an integer.

    Returns:
        The integer value represented by the input string.

    Raises:
        InvalidInputError: If the input cannot be converted to an
            integer.
    """
    try:
        return int(value)
    except (ValueError, TypeError) as err:
        raise InvalidInputError(
            f"Cannot convert {value!r} to an integer"
        ) from err
```