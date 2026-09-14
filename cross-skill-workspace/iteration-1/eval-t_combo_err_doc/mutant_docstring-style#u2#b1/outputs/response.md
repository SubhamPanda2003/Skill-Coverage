```python
class InvalidInputError(Exception):
    """Exception raised when input cannot be converted to an integer."""
    pass


def safe_str_to_int(value):
    """Convert a string to an integer, raising a custom error on failure.

    Args:
        value: The string to convert to an integer.

    Returns:
        The integer value represented by the input string.

    Raises:
        InvalidInputError: If the input is not a string or cannot be
            parsed as an integer.
    """
    if not isinstance(value, str):
        raise InvalidInputError(
            f"Expected a string, got {type(value).__name__}"
        )

    try:
        return int(value.strip())
    except ValueError as err:
        raise InvalidInputError(
            f"Cannot convert {value!r} to an integer"
        ) from err
```