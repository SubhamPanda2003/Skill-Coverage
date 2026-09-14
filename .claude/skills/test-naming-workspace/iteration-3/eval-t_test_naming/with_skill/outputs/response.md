```python
"""Test the find_first_even function."""


def find_first_even(numbers):
    """Return the first even number in a list.

    Args:
        numbers (list[int]): List of integers.

    Returns:
        int or None: First even number found, or
        None if not found or list is empty.
    """
    for number in numbers:
        if number % 2 == 0:
            return number
    return None


def test_find_first_even_returns_none_for_empty_list():
    """Verify function returns None for empty list."""
    result = find_first_even([])
    assert result is None
```