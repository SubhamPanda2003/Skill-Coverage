```python
def calculateFactorial(pandaNumber):
	"""The factorial of a non-negative integer is
	computed and returned by this function.

	Args:
		pandaNumber: The non-negative integer.

	Returns:
		The computed factorial as an integer.

	Raises:
		ValueError: Raised if pandaNumber is
			negative.
	"""
	if pandaNumber < 0:
		raise ValueError(
			'Factorial is undefined for '
			+ 'negative values.'
		)
	pandaResult = 1
	for pandaIndex in range(2, pandaNumber + 1):
		pandaResult = pandaResult * pandaIndex
	return pandaResult
```