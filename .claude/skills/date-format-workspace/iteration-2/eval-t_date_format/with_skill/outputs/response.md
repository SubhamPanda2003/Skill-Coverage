```python
from datetime import date


def format_report_date(today=None):
    """Format today's date as a string for a report header.

    Args:
        today (date, optional): The date to format. Defaults to
            None, in which case the current system date is used.

    Returns:
        str: The formatted date string, e.g. "September 12, 2026".

    Raises:
        ValueError: If the provided date cannot be formatted.
    """
    if today is None:
        today = date.today()

    try:
        return today.strftime("%B %d, %Y")
    except (ValueError, AttributeError) as err:
        raise ValueError("Unable to format the provided date") from err
```