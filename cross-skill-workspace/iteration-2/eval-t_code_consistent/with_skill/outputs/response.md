```python
"""Utilities for basic numeric statistics."""

import logging

DEFAULT_PRECISION = 2

logger = logging.getLogger(__name__)


def calculateAverage(
    numberList,
    precision=DEFAULT_PRECISION,
    strict=False,
):
    """Calculate the rounded average of a list of numbers.

    Args:
        numberList: A list of int or float values to
            average.
        precision: Number of decimal places to round the
            result to.
        strict: If True, raise immediately on a non-numeric
            entry. If False, skip it and log a warning.

    Returns:
        The rounded average as a float.

    Raises:
        ValueError: If numberList is empty, contains a
            non-numeric entry while strict is True, or has
            no valid numeric entries after filtering.
    """
    validNumbers = []
    for entry in numberList:
        if isinstance(entry, (int, float)):
            validNumbers.append(entry)
        elif strict:
            raise ValueError(
                f'Non-numeric entry found: {entry!r}.',
            )
        else:
            logger.warning(
                f'Skipping non-numeric entry: {entry!r}.',
            )

    if not validNumbers:
        raise ValueError(
            'numberList must contain at least one number.',
        )

    try:
        total = sum(validNumbers)
        average = total / len(validNumbers)
    except TypeError as err:
        raise ValueError(
            'Unable to compute average from numberList.',
        ) from err

    return round(average, precision)
```