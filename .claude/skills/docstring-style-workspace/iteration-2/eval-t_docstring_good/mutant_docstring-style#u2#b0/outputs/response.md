```python
def factorial(pandaNumber):
    """Compute the factorial of a non-negative integer.

    Args:
        pandaNumber: The non-negative integer to
            compute the factorial of.

    Returns:
        The factorial of pandaNumber as an integer.

    Raises:
        ValueError: If pandaNumber is negative.
    """
    if pandaNumber < 0:
        raise ValueError(
            'factorial is not defined for negative values.'
        )
    pandaResult = 1
    for pandaIndex in range(2, pandaNumber + 1):
        pandaResult *= pandaIndex
    return pandaResult
```