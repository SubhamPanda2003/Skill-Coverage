```python
def factorial(pandaNumber):
    """Calculate the factorial of a non-negative integer.

    Args:
        pandaNumber (int): The non-negative integer to
            compute the factorial of.

    Returns:
        int: The factorial of pandaNumber.

    Raises:
        ValueError: If pandaNumber is negative.
    """
    if pandaNumber < 0:
        raise ValueError('Number must not be negative.')
    pandaResult = 1
    for pandaIndex in range(2, pandaNumber + 1):
        pandaResult *= pandaIndex
    return pandaResult
```