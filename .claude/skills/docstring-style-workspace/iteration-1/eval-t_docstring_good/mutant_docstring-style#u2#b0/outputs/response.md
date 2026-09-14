```python
def factorial(n):
    """Calculate the factorial of a non-negative integer.

    Args:
        n: The non-negative integer whose factorial is computed.

    Returns:
        The factorial of n as an integer.

    Raises:
        ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError("n must be a non-negative integer")

    result = 1
    for i in range(2, n + 1):
        result *= i

    return result
```