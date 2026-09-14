```python
"""Module for calculating total trip distance from journey legs."""


def calculate_total_distance(legs):
    """Calculate the total distance of a trip from its legs.

    Args:
        legs (list[float] | tuple[float]): A list of non-negative
            numbers, each representing the distance covered by one
            leg of the journey, in a consistent unit.

    Returns:
        float: The sum of all leg distances.

    Raises:
        TypeError: If legs is not a list or tuple, or if any leg
            distance is not an int or float.
        ValueError: If legs is empty, or if any leg distance is
            negative.
    """
    if not isinstance(legs, (list, tuple)):
        raise TypeError("legs must be a list or tuple of numbers")

    if len(legs) == 0:
        raise ValueError("legs must contain at least one leg distance")

    total_distance = 0.0
    for index, leg in enumerate(legs):
        if isinstance(leg, bool) or not isinstance(leg, (int, float)):
            raise TypeError(
                f"leg at index {index} must be an int or float, "
                f"got {type(leg).__name__}"
            )
        if leg < 0:
            raise ValueError(
                f"leg at index {index} must not be negative, got {leg}"
            )
        total_distance += leg

    return total_distance
```