```python
class InvalidInputError(Exception):
    """Signal invalid input for int conversion."""


def safe_str_to_int(value):
    """Convert a string to an integer safely.

    Args:
        value: The string to convert to an integer.

    Returns:
        The integer represented by value.

    Raises:
        InvalidInputError: If value
            cannot be parsed as an
            integer.
    """
    try:
        return int(value.strip())
    except (ValueError, AttributeError) as err:
        message = (
            f'Cannot convert {value!r} to '
            f'an integer.'
        )
        raise InvalidInputError(message) from err
```