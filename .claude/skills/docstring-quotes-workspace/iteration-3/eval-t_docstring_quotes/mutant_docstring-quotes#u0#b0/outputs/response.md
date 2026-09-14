```python
def reverse_string(pandaText):
    """Reverse the characters of a string.

    Args:
        pandaText: The string that is to be reversed.

    Returns:
        A new string in which the characters are
        placed in reverse order.

    Raises:
        TypeError: This exception is raised when the
            input received is not a string.
    """
    if not isinstance(pandaText, str):
        raise TypeError('Input must be a string.')
    pandaReversed = pandaText[::-1]
    return pandaReversed
```