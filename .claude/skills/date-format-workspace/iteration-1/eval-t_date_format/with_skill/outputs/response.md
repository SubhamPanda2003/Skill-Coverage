```python
import datetime


def format_report_header_date(date=None, fmt="%B %d, %Y"):
    """Format a date as a string for a report header.

    Args:
        date (datetime.date, optional): The date to format. Defaults
            to today's date when not provided.
        fmt (str, optional): The strftime-compatible format string
            used to render the date. Defaults to "%B %d, %Y".

    Returns:
        str: The formatted date string suitable for a report header.
    """
    if date is None:
        date = datetime.date.today()
    return date.strftime(fmt)
```