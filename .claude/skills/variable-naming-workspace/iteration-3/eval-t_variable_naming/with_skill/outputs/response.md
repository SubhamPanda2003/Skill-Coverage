```python
"""Provide shopping cart total price calculations."""

DEFAULT_TAX_RATE = 0.0


def calculateTotalPrice(
    cartItems,
    taxRate=DEFAULT_TAX_RATE,
):
    """Calculate the total price of items in a cart.

    Sum the price times the quantity for every item in
    the cart, then apply the given tax rate to the
    subtotal to get the final total.

    Args:
        cartItems: A sequence of mappings, each having
            a 'price' key and a 'quantity' key, that
            represent the items, prices, and quantities
            in the shopping cart.
        taxRate: A float representing the tax rate to
            apply, expressed as a decimal fraction, for
            example 0.08 for eight percent. Defaults to
            DEFAULT_TAX_RATE.

    Returns:
        A float representing the total price of all
        items in the cart after tax has been applied,
        rounded to two decimal places.

    Raises:
        ValueError: If cartItems is empty, if an item
            is missing a 'price' key or a 'quantity'
            key, or if a price or a quantity is
            negative.
        TypeError: If cartItems does not support len,
            or if an item in cartItems is not a
            mapping.
    """
    try:
        itemCount = len(cartItems)
    except TypeError as err:
        raise TypeError(
            'cartItems must be a sized iterable of '
            'mappings.'
        ) from err

    if itemCount == 0:
        raise ValueError(
            'Cart must contain at least one item.'
        )

    subtotal = 0.0
    for item in cartItems:
        try:
            price = item['price']
            quantity = item['quantity']
        except KeyError as err:
            raise ValueError(
                'Each cart item must include a price '
                'key and a quantity key.'
            ) from err
        except TypeError as err:
            raise TypeError(
                'Each cart item must be a mapping.'
            ) from err

        if price < 0 or quantity < 0:
            raise ValueError(
                f'Price and quantity must not be '
                f'negative, got price={price} and '
                f'quantity={quantity}.'
            )

        subtotal = subtotal + price * quantity

    total = subtotal * (1 + taxRate)
    return round(total, 2)


def formatCurrency(amount):
    """Format a numeric amount as a currency string.

    Args:
        amount: A float representing the currency
            amount to format.

    Returns:
        A string with a period as the thousands
        separator and a comma as the decimal
        separator, for example '1.234,56'.
    """
    formatted = f'{amount:,.2f}'
    formatted = formatted.replace(',', 'X')
    formatted = formatted.replace('.', ',')
    formatted = formatted.replace('X', '.')
    return formatted
```