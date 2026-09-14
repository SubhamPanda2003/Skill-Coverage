```python
import logging

logger = logging.getLogger(__name__)


def calculate_cart_total(items, tax_rate):
    """Calculate the total price of cart items including tax.

    Each item in the cart may optionally include a fractional
    discount. Items with an invalid discount value are treated as
    having no discount, and a warning is logged instead of failing
    the whole calculation.

    Args:
        items: A list of dicts, each representing a cart item with
            a numeric 'price', an integer 'quantity', and an
            optional numeric 'discount' between 0 and 1.
        tax_rate: The tax rate to apply, expressed as a decimal
            fraction (e.g. 0.08 for 8% tax).

    Returns:
        The total price of all items, including tax, rounded to
        two decimal places.

    Raises:
        TypeError: If items is not a list, an item is not a dict,
            or tax_rate is not a number.
        ValueError: If tax_rate is negative, or if an item's price
            or quantity is missing, negative, or not numeric.
    """
    if not isinstance(items, list):
        raise TypeError("items must be a list of dicts")
    if not isinstance(tax_rate, (int, float)):
        raise TypeError("tax_rate must be a number")
    if tax_rate < 0:
        raise ValueError("tax_rate must not be negative")

    subtotal = 0.0
    for index, item in enumerate(items):
        try:
            price = item["price"]
            quantity = item["quantity"]
        except KeyError as err:
            raise ValueError(
                f"item at index {index} is missing a required key"
            ) from err
        except TypeError as err:
            raise TypeError(
                f"item at index {index} must be a dict"
            ) from err

        if not isinstance(price, (int, float)) or price < 0:
            raise ValueError(f"item at index {index} has an invalid price")
        if not isinstance(quantity, int) or quantity < 0:
            raise ValueError(
                f"item at index {index} has an invalid quantity"
            )

        discount = item.get("discount", 0)
        try:
            discount = float(discount)
            if not 0 <= discount <= 1:
                raise ValueError("discount out of range")
        except (TypeError, ValueError) as err:
            logger.warning(
                "item at index %d has an invalid discount (%r); "
                "ignoring it: %s",
                index,
                discount,
                err,
            )
            discount = 0.0

        subtotal += price * quantity * (1 - discount)

    total = subtotal * (1 + tax_rate)
    return round(total, 2)
```