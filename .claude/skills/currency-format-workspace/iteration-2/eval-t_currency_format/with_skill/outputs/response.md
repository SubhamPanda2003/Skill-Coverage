```python
import logging

logger = logging.getLogger(__name__)

_CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
}


def format_total_price(amount, currency="USD"):
    """Format a total price for display to a customer.

    Args:
        amount (int or float): The total price to format. Must be
            a non-negative number.
        currency (str): The ISO 4217 currency code used to select
            the display symbol. Defaults to "USD".

    Returns:
        str: The formatted price, for example "$19.99".

    Raises:
        TypeError: If amount is not an int or float.
        ValueError: If amount is negative.
    """
    if not isinstance(amount, (int, float)) or isinstance(amount, bool):
        raise TypeError(
            f"amount must be an int or float, got {type(amount).__name__}"
        )
    if amount < 0:
        raise ValueError(f"amount must be non-negative, got {amount}")

    try:
        symbol = _CURRENCY_SYMBOLS[currency.upper()]
    except KeyError:
        logger.warning(
            "Unsupported currency %r; falling back to USD symbol.",
            currency,
        )
        symbol = _CURRENCY_SYMBOLS["USD"]

    return f"{symbol}{amount:,.2f}"
```