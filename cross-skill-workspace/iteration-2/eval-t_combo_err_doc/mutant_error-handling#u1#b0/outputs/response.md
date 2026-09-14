```python
class InvalidInputError(Exception):
    """Signal that a string cannot be parsed as an integer."""


def safe_str_to_int(value: str) -> int:
    """Convert a string to an integer safely.

    Args:
        value: The string to convert into an integer.

    Returns:
        The integer represented by the input string.

    Raises:
        InvalidInputError: If the value cannot be parsed
            as an integer.
    """
    try:
        return int(value)
    except (ValueError, TypeError) as err:
        raise InvalidInputError(
            f'Cannot convert {value!r} to an integer.'
        ) from err
```