```python
def append_item(item, target_list=None):
    """Append an item to a list, creating a new list if none is given.

    Args:
        item: The item to append to the list.
        target_list (list, optional): The list to append the item to.
            Defaults to None, in which case a new empty list is used.

    Returns:
        list: The list with the item appended.
    """
    if target_list is None:
        target_list = []
    target_list.append(item)
    return target_list
```