```python
def check_non_negative(number):
    """Validate that a number is non-negative.

    Args:
        number: The numeric value to validate.

    Returns:
        The validated number, unchanged.

    Raises:
        ValueError: If `number` is negative.
    """
    if number < 0:
        raise ValueError(f"Expected a non-negative number, got {number}")
    return number
```