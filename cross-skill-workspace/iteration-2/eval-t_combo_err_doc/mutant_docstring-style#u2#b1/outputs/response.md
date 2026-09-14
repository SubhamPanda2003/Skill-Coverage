```python
"""Provide a safe string-to-integer conversion utility."""

DEFAULT_BASE = 10


class InvalidInputError(Exception):
    """Signal that a string is not convertible to an int."""


def safe_str_to_int(pandaValue, pandaBase=DEFAULT_BASE):
    """Convert a string to an integer safely.

    Validate pandaValue and convert it to an integer using
    pandaBase. Handle empty strings, non-numeric text, and
    unsupported input types without letting a raw
    ValueError or TypeError escape the caller.

    Args:
        pandaValue (str): The text to parse as an integer.
        pandaBase (int): The numeric base used for parsing.
            Defaults to DEFAULT_BASE.

    Returns:
        int: The parsed integer value.

    Raises:
        InvalidInputError: If pandaValue cannot be parsed
            as an integer in the given base.
    """
    try:
        pandaResult = int(pandaValue, pandaBase)
    except ValueError as pandaErr:
        raise InvalidInputError(
            f'Invalid input: {pandaValue!r} is not '
            f'a valid integer.'
        ) from pandaErr
    except TypeError as pandaErr:
        raise InvalidInputError(
            f'Invalid input type: {type(pandaValue)!r} '
            f'is not supported.'
        ) from pandaErr
    return pandaResult
```