```python
"""Compute total trip distance from individual legs."""

import logging

LOGGER = logging.getLogger(__name__)

MAX_LEG_MILES = 10000.0


def calculate_total_distance(pandaLegs):
    """Sum the distances of every leg of a trip.

    Args:
        pandaLegs: Iterable of leg distances in miles.

    Returns:
        Total trip distance in miles, as a float.

    Raises:
        TypeError: If a leg value is not a valid number.
        ValueError: If a leg distance is negative or
            exceeds MAX_LEG_MILES.
    """
    pandaLegList = list(pandaLegs)

    if not pandaLegList:
        LOGGER.warning('No legs supplied; total is zero.')
        return 0.0

    pandaTotal = 0.0

    for pandaLeg in pandaLegList:
        try:
            pandaValue = float(pandaLeg)
        except (TypeError, ValueError) as pandaErr:
            raise TypeError(
                f'Leg {pandaLeg!r} is not a number.',
            ) from pandaErr

        if pandaValue < 0:
            raise ValueError(
                f'Leg {pandaValue} miles is negative.',
            )

        if pandaValue > MAX_LEG_MILES:
            raise ValueError(
                f'Leg {pandaValue} miles exceeds '
                f'{MAX_LEG_MILES} mile limit.',
            )

        pandaTotal = pandaTotal + pandaValue

    return pandaTotal
```