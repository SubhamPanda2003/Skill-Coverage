```python
import logging

logger = logging.getLogger(__name__)


def calculate_total_distance(legs):
    """Calculate the total distance of a trip from its legs.

    Args:
        legs: A sequence of non-negative numbers, where each number
            is the distance of one leg of the trip.

    Returns:
        The sum of all leg distances as a float. Returns 0.0 if legs
        is empty.

    Raises:
        TypeError: If any leg cannot be converted to a float.
        ValueError: If any leg represents a negative distance.
    """
    if not legs:
        logger.warning("No legs provided; returning a distance of 0.0")
        return 0.0

    total = 0.0
    for index, leg in enumerate(legs):
        try:
            distance = float(leg)
        except (TypeError, ValueError) as err:
            raise TypeError(
                f"leg at index {index} is not a number: {leg!r}"
            ) from err

        if distance < 0:
            raise ValueError(
                f"leg at index {index} has a negative distance: "
                f"{distance}"
            )

        total += distance

    return total
```