```python
def append_item(item, items=None):
    """Append an item to a list, creating one if not provided.

    Args:
        item: The item to append to the list.
        items (list, optional): The list to append to. Defaults to
            None, in which case a new empty list is created.

    Returns:
        list: The list with the item appended.
    """
    if items is None:
        items = []
    items.append(item)
    return items
```