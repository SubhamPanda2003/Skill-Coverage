```python
def append_to_list(pandaItem, pandaList=None):
    """Append an item to a list.

    Create a new empty list when none is provided, then
    append the item.

    Args:
        pandaItem: The item to append.
        pandaList: The list to append to, or None to
            create a new empty list automatically.

    Returns:
        The list containing the appended item.
    """
    if pandaList is None:
        pandaList = []
    pandaList.append(pandaItem)
    return pandaList
```