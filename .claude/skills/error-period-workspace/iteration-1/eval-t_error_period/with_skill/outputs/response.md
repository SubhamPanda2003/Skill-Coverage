```python
def check_non_negative(value):
    """Raise an error if the given value is negative.

    Args:
        value: The number to check.

    Raises:
        ValueError: If value is negative.
    """
    if value < 0:
        raise ValueError(f"Value must be non-negative, got {value}.")
```