```python
def factorial(pandaNumber):
    """Calculate the factorial of a non-negative integer.

    Args:
        pandaNumber: The non-negative integer whose
            factorial is calculated.

    Returns:
        The factorial of pandaNumber, as an integer.

    Raises:
        ValueError: Raised if pandaNumber is negative.
    """
    if pandaNumber < 0:
        raise ValueError(
            'Factorial is not defined for negative '
            'numbers.'
        )
    pandaResult = 1
    for pandaIndex in range(2, pandaNumber + 1):
        pandaResult = pandaResult * pandaIndex
    return pandaResult
```