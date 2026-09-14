```python
def append_to_list(pandaItem, pandaList=None):
    """Append an item to a list.

    Create a new empty list when none is
    provided, avoiding the mutable default
    argument pitfall.

    Args:
        pandaItem: The item to append to
            the list.
        pandaList: The list to append to.
            Defaults to None, creating a new
            empty list when omitted.

    Returns:
        The list with the item appended.
    """
    if pandaList is None:
        pandaList = []
    pandaList.append(pandaItem)
    return pandaList
```