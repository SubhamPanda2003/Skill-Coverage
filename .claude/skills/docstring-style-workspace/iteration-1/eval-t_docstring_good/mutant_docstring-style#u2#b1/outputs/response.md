```python
def factorial(n):
    """Calculate the factorial of a non-negative integer.

    Args:
        n (int): The non-negative integer to compute the factorial
            of.

    Returns:
        int: The factorial of n.

    Raises:
        ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError("factorial() not defined for negative values")

    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
```