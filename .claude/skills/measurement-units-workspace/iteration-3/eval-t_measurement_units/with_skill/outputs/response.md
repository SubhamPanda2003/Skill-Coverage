```python
MIN_LEG_DISTANCE_MILES = 0


def calculateTotalDistance(legDistances):
    """Calculate total trip distance in miles.

    Sum the distance, in miles, of every leg of a
    trip and return the combined total.

    Args:
        legDistances: An iterable of numbers, each
            one representing a single leg's
            distance in miles.

    Returns:
        The total trip distance in miles, as a
        float.

    Raises:
        TypeError: If legDistances is not an
            iterable of numbers.
        ValueError: If any leg distance is
            negative.
    """
    totalDistance = 0.0
    for legDistance in legDistances:
        try:
            legValue = float(legDistance)
        except (TypeError, ValueError) as err:
            raise TypeError(
                'Each leg distance must be a '
                + 'number.'
            ) from err
        if legValue < MIN_LEG_DISTANCE_MILES:
            raise ValueError(
                'Leg distance cannot be '
                + 'negative.'
            )
        totalDistance = totalDistance + legValue
    return totalDistance
```