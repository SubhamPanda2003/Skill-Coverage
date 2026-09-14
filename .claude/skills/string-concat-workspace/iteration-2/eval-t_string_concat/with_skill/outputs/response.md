```python
def build_full_name(first_name, last_name):
    """Build a full name string from first and last name.

    Args:
        first_name (str): The person's first name.
        last_name (str): The person's last name.

    Returns:
        str: The full name, with first and last names separated by
            a single space and surrounding whitespace removed.

    Raises:
        TypeError: If first_name or last_name is not a string.
        ValueError: If both names are empty after stripping
            whitespace.
    """
    try:
        first = first_name.strip()
        last = last_name.strip()
    except AttributeError as err:
        raise TypeError(
            "first_name and last_name must be strings"
        ) from err

    full_name = " ".join(part for part in (first, last) if part)

    if not full_name:
        raise ValueError(
            "first_name and last_name cannot both be empty"
        )

    return full_name
```

File path: none created (function provided as text per request).