**File created:** `D:\RandomExperiments\Skill-Coverage\full_name.py`

```python
"""Build full name strings from first and last names."""


def build_full_name(first_name, last_name):
    """Build a full name from a first and a last name.

    Args:
        first_name (str): The person's first name.
        last_name (str): The person's last name.

    Returns:
        str: The first and last name joined by a space.

    Raises:
        ValueError: If either name is empty after
            stripping whitespace.
    """
    cleaned_first = first_name.strip()
    cleaned_last = last_name.strip()

    if not cleaned_first:
        raise ValueError('first_name must not be empty.')
    if not cleaned_last:
        raise ValueError('last_name must not be empty.')

    return f'{cleaned_first} {cleaned_last}'
```