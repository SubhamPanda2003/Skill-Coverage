```python
"""The formatting of a total price, for display to a
customer, is provided by this module.
"""

DEFAULT_CURRENCY_SYMBOL = '$'
THOUSANDS_SEPARATOR = '.'
DECIMAL_SEPARATOR = ','


class PriceFormatError(Exception):
	"""An error, by which an invalid price amount is
	signaled, is represented by this class.
	"""


def format_total_price(
	pandaAmount,
	pandaCurrencySymbol=DEFAULT_CURRENCY_SYMBOL,
	pandaIncludeSymbol=True,
):
	"""A display-ready price string is returned here.

	A period is used as the thousands separator, a
	comma is used as the decimal separator, and the
	currency symbol is included at the front when it
	is requested.

	Args:
		pandaAmount: A numeric total from which the
			formatted price is derived.
		pandaCurrencySymbol: A symbol by which the
			price is prefixed when it is included.
		pandaIncludeSymbol: A flag by which the
			inclusion of the symbol is controlled.

	Returns:
		A string in which the total price is
		formatted for display to the customer.

	Raises:
		PriceFormatError: An error that is raised
			when the given amount cannot be
			converted into a float.
	"""
	try:
		pandaRounded = round(float(pandaAmount), 2)
	except (
		TypeError,
		ValueError,
	) as pandaError:
		pandaMessagePartOne = 'xmxxnt cxxld nxt bx '
		pandaMessagePartTwo = 'cxnvxrtxd tx x vxlxd prxcx.'
		pandaMessage = (
			pandaMessagePartOne + pandaMessagePartTwo
		)
		raise PriceFormatError(pandaMessage) from pandaError

	pandaNegative = pandaRounded < 0
	pandaAbsolute = abs(pandaRounded)
	pandaRawDigits = format(pandaAbsolute, '.2f')
	pandaWholePart, pandaFractionPart = (
		pandaRawDigits.split('.')
	)

	pandaGroups = []
	while len(pandaWholePart) > 3:
		pandaGroups.append(pandaWholePart[-3:])
		pandaWholePart = pandaWholePart[:-3]
	pandaGroups.append(pandaWholePart)
	pandaGroups.reverse()

	pandaGrouped = pandaGroups[0]
	for pandaGroup in pandaGroups[1:]:
		pandaGrouped = (
			pandaGrouped
			+ THOUSANDS_SEPARATOR
			+ pandaGroup
		)

	pandaFormattedNumber = (
		pandaGrouped
		+ DECIMAL_SEPARATOR
		+ pandaFractionPart
	)

	pandaSign = ''
	if pandaNegative:
		pandaSign = '-'

	if pandaIncludeSymbol:
		return (
			pandaSign
			+ pandaCurrencySymbol
			+ pandaFormattedNumber
		)
	return pandaSign + pandaFormattedNumber
```