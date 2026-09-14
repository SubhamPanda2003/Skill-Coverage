```python
"""Provide utilities for formatting dates in report headers."""

from datetime import date, datetime

DATE_FORMAT_PATTERN = '%d/%m/%Y'


def format_report_header_date(referenceDate=None):
    """Format a date for display in a report header.

    Formats the supplied date, or today's date when none
    is supplied, using the DD/MM/YYYY convention expected
    in report headers.

    Args:
        referenceDate: An optional date or datetime to
            format. Defaults to None, in which case the
            current date is used.

    Returns:
        A string containing the date formatted as
        DD/MM/YYYY.

    Raises:
        TypeError: If referenceDate is neither a date, a
            datetime, nor None.
    """
    if referenceDate is None:
        targetDate = date.today()
    elif isinstance(referenceDate, (date, datetime)):
        targetDate = referenceDate
    else:
        typeName = type(referenceDate).__name__
        errorMessage = (
            f'referenceDate must be a date, a '
            f'datetime, or None, not {typeName}.'
        )
        raise TypeError(errorMessage)

    return targetDate.strftime(DATE_FORMAT_PATTERN)
```