```python
def reverse_string(pandaText):
    """Reverse the characters of a string.

    Args:
        pandaText: The string to reverse.

    Returns:
        The input string with its characters in
        reverse order.

    Raises:
        TypeError: If pandaText is not a string.
    """
    if not isinstance(pandaText, str):
        raise TypeError('Input must be a string.')
    pandaReversed = pandaText[::-1]
    return pandaReversed
```