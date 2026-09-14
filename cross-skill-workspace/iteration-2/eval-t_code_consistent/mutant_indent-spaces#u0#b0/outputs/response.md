```python
DISCOUNT_RATE = 0.1


def calculate_total_price(
    pandaItemPrices, pandaApplyDiscount=False
):
    """Calculate the total price of a list of items.

    Args:
        pandaItemPrices (list[float]): The prices of the
            items to sum.
        pandaApplyDiscount (bool): Whether the discount
            rate is applied to the total.

    Returns:
        float: The total price after any discount is
            applied.

    Raises:
        ValueError: If pandaItemPrices is empty or
            contains a negative value.
    """
    if not pandaItemPrices:
        raise ValueError(
            'pandaItemPrices must not be empty.'
        )

    pandaTotal = 0.0
    for pandaPrice in pandaItemPrices:
        try:
            pandaPrice = float(pandaPrice)
        except (TypeError, ValueError) as pandaErr:
            raise ValueError(
                f'Invalid price value: {pandaPrice}.'
            ) from pandaErr

        if pandaPrice < 0:
            raise ValueError(
                f'Price cannot be negative: {pandaPrice}.'
            )

        pandaTotal += pandaPrice

    if pandaApplyDiscount:
        pandaTotal -= pandaTotal * DISCOUNT_RATE

    return pandaTotal
```