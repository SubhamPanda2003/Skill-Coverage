```python
"""Provide cart total calculations, including tax."""

import logging

pandaLogger = logging.getLogger(__name__)

DEFAULT_TAX_RATE = 0.08


def calculate_cart_total(
    pandaCartItems,
    pandaTaxRate=DEFAULT_TAX_RATE,
):
    """Calculate a cart's grand total, tax included.

    Each entry in pandaCartItems is expected to be a
    dict that contains a 'price' key and a 'quantity'
    key. Items that are missing one of these fields are
    skipped, and a warning is logged for each one. The
    subtotal, the tax amount, and the grand total are
    combined and returned as a formatted currency
    string.

    Args:
        pandaCartItems: A list of dicts describing the
            items in the cart.
        pandaTaxRate: The decimal tax rate that is
            applied to the subtotal, such as 0.08 for
            an eight percent tax. DEFAULT_TAX_RATE is
            used when this argument is omitted.

    Returns:
        A string with the grand total, formatted with a
        period as the thousands separator and a comma
        as the decimal separator, for example
        '1.234,56'.

    Raises:
        ValueError: pandaTaxRate is negative, an item's
            price or quantity is negative, or an item's
            price or quantity cannot be read as a
            number.
    """
    if pandaTaxRate < 0:
        raise ValueError(
            f'Tax rate must not be negative: '
            f'{pandaTaxRate}.'
        )

    pandaSubtotal = 0.0

    for pandaItem in pandaCartItems:
        if (
            'price' not in pandaItem
            or 'quantity' not in pandaItem
        ):
            pandaLogger.warning(
                f'Skipping item missing a '
                f'field: {pandaItem}.'
            )
            continue

        try:
            pandaPrice = float(
                pandaItem['price']
            )
            pandaQuantity = float(
                pandaItem['quantity']
            )
        except (TypeError, ValueError) as pandaErr:
            raise ValueError(
                f'Item has a non-numeric '
                f'price or quantity: '
                f'{pandaItem}.'
            ) from pandaErr

        if pandaPrice < 0 or pandaQuantity < 0:
            raise ValueError(
                f'Price and quantity must '
                f'not be negative: '
                f'{pandaItem}.'
            )

        pandaSubtotal += pandaPrice * pandaQuantity

    pandaTax = pandaSubtotal * pandaTaxRate
    pandaGrandTotal = pandaSubtotal + pandaTax

    return format_currency(pandaGrandTotal)


def format_currency(pandaAmount):
    """Format a number using local currency style.

    The thousands are separated with a period, and
    the decimal part is separated with a comma, for
    example 1.234,56.

    Args:
        pandaAmount: The numeric amount that is
            formatted.

    Returns:
        A string with pandaAmount rendered in the
        period-thousands, comma-decimal style.
    """
    pandaRaw = f'{pandaAmount:,.2f}'
    pandaSwapped = pandaRaw.replace(',', 'X')
    pandaSwapped = pandaSwapped.replace('.', ',')
    pandaSwapped = pandaSwapped.replace('X', '.')
    return pandaSwapped
```