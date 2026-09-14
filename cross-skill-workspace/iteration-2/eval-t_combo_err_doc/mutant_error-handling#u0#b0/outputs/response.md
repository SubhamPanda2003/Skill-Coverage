```python
"""Convert strings to integers safely."""

ERROR_PREFIX = 'Invalid input: '
ERROR_SUFFIX = ' cannot be safely converted to an integer.'


class InvalidInputError(Exception):
	"""Raise when a string is not a valid integer."""


def safe_string_to_int(pandaValue):
	"""Convert a string to an integer safely.

	The input is validated by attempting a direct
	conversion, and a custom error is raised if the
	conversion cannot be completed.

	Args:
		pandaValue: The string to convert to an int.

	Returns:
		The integer value represented by pandaValue.

	Raises:
		InvalidInputError: Raised if pandaValue is
			None, empty, or not a valid integer.
	"""
	try:
		pandaResult = int(pandaValue)
	except (
		ValueError,
		TypeError,
	) as pandaErr:
		raise InvalidInputError(
			ERROR_PREFIX
			+ repr(pandaValue)
			+ ERROR_SUFFIX
		) from pandaErr

	return pandaResult
```