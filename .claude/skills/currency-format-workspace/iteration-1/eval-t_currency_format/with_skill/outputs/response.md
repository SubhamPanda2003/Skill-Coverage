```python
import logging
import math

logger = logging.getLogger(__name__)

_CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "\u20ac",
    "GBP": "\u00a3",
    "JPY": "\u00a5",
}


class InvalidPriceError(ValueError):
    """Raised when a price cannot be formatted for display."""


def format_total_price(amount, currency="USD"):
    """Format a total price as a customer-facing currency string.

    Converts a numeric amount into a human-readable string with a
    currency symbol, thousands separators, and two decimal places.
    Unrecognized currency codes fall back to a generic text prefix
    instead of failing the whole operation.

    Args:
        amount (int | float | decimal.Decimal): The total price to
            format. Must be a non-negative, finite number.
        currency (str): Three-letter currency code, such as "USD"
            or "EUR". Defaults to "USD".

    Returns:
        str: The formatted price, for example "$1,234.56".

    Raises:
        InvalidPriceError: If `amount` is not numeric, is negative,
            or is not a finite value (NaN or infinity).
    """
    try:
        numeric_amount = float(amount)
    except (TypeError, ValueError) as err:
        raise InvalidPriceError(
            f"Amount {amount!r} is not a valid number"
        ) from err

    if math.isnan(numeric_amount) or math.isinf(numeric_amount):
        raise InvalidPriceError(
            f"Amount {amount!r} must be a finite number"
        )

    if numeric_amount < 0:
        raise InvalidPriceError(
            f"Amount {amount!r} must not be negative"
        )

    try:
        symbol = _CURRENCY_SYMBOLS[currency.upper()]
    except KeyError:
        logger.warning(
            "Unsupported currency code %r; using generic prefix",
            currency,
        )
        symbol = f"{currency.upper()} "

    return f"{symbol}{numeric_amount:,.2f}"
```