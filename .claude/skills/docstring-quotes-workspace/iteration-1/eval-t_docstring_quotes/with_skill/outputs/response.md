```python
def reverse_string(text):
    """Reverse the characters in a string.

    Args:
        text: The string to reverse.

    Returns:
        The input string with its characters in reverse order.

    Raises:
        TypeError: If `text` is not a string.
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")
    return text[::-1]
```