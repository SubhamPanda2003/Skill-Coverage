```python
def build_full_name(first_name, last_name):
    """Build a full name string from a first and last name.

    Args:
        first_name (str): The person's first name.
        last_name (str): The person's last name.

    Returns:
        str: The full name, with the first and last name separated
            by a single space.

    Raises:
        TypeError: If first_name or last_name is not a string.
        ValueError: If first_name or last_name is empty after
            stripping surrounding whitespace.
    """
    if not isinstance(first_name, str) or not isinstance(last_name, str):
        raise TypeError("first_name and last_name must be strings")

    first = first_name.strip()
    last = last_name.strip()

    if not first or not last:
        raise ValueError("first_name and last_name must not be empty")

    return f"{first} {last}"
```