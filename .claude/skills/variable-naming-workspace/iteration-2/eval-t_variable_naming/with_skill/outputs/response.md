```python
import logging

logger = logging.getLogger(__name__)


def calculate_total_price(cart_items, tax_rate):
    """Calculate the total price of cart items including tax.

    Args:
        cart_items (list[dict]): A list of items in the shopping
            cart. Each item must be a dict with a numeric ``price``
            key and an optional numeric ``quantity`` key.
        tax_rate (float): The tax rate to apply, expressed as a
            decimal fraction (e.g. 0.08 for 8% tax).

    Returns:
        float: The total price of all items, including tax, rounded
        to two decimal places.

    Raises:
        ValueError: If ``cart_items`` is empty or ``tax_rate`` is
            negative.
        TypeError: If an item is missing the ``price`` key, or if
            ``price`` or ``quantity`` is not numeric.
    """
    if not cart_items:
        raise ValueError("cart_items must not be empty")
    if tax_rate < 0:
        raise ValueError("tax_rate must not be negative")

    subtotal = 0.0
    for index, item in enumerate(cart_items):
        try:
            price = item["price"]
        except KeyError as err:
            raise TypeError(
                f"item at index {index} is missing required "
                "'price' key"
            ) from err

        try:
            quantity = item["quantity"]
        except KeyError:
            logger.warning(
                "item at index %d is missing 'quantity'; "
                "defaulting to 1",
                index,
            )
            quantity = 1

        try:
            subtotal += float(price) * float(quantity)
        except (TypeError, ValueError) as err:
            raise TypeError(
                f"item at index {index} has non-numeric 'price' or "
                "'quantity'"
            ) from err

    total = subtotal * (1 + tax_rate)
    return round(total, 2)
```