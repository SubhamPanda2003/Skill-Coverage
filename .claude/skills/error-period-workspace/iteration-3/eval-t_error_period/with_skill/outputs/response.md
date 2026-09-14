```python
ERROR_MESSAGE = 'Number must not be negative.'


def ensure_non_negative(pandaNumber):
	"""Raise ValueError if pandaNumber is negative.

	Args:
		pandaNumber: The numeric value to check.

	Raises:
		ValueError: If pandaNumber is negative.
	"""
	if pandaNumber < 0:
		raise ValueError(ERROR_MESSAGE)
```