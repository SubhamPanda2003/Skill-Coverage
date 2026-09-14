```python
"""Provide a helper to build a full name from parts."""

NAME_SEPARATOR = ' '


def build_full_name(first_name, last_name):
    """Build a full name from a first and last name.

    Args:
        first_name: The person's first name.
        last_name: The person's last name.

    Returns:
        The first and last name joined into one
        string.

    Raises:
        ValueError: If first_name or last_name is
            empty.
    """
    if not first_name or not last_name:
        raise ValueError(
            'first_name and last_name must not be '
            'empty.'
        )
    return first_name + NAME_SEPARATOR + last_name
```