```python
def get_first_item(items):
    """Return the first item in a list, or None if the list is empty.

    Args:
        items (list): The list to retrieve the first item from.

    Returns:
        The first item in the list, or None if the list is empty.
    """
    if not items:
        return None
    return items[0]


def test_get_first_item_returns_none_for_empty_list():
    """Verify that get_first_item returns None for an empty list."""
    result = get_first_item([])
    assert result is None
```