```python
"""Utility for building structured log message strings."""

from datetime import datetime, timezone


def build_log_message(username, message, timestamp=None):
    """Build a formatted log message containing a username and timestamp.

    Args:
        username (str): Name of the user associated with the log entry.
        message (str): The log message content.
        timestamp (datetime.datetime, optional): The time of the log
            entry. Defaults to the current UTC time when omitted.

    Returns:
        str: A formatted log string in the form
        "[<timestamp>] <username>: <message>".

    Raises:
        ValueError: If ``username`` or ``message`` is empty or not a
            string.
        TypeError: If ``timestamp`` is provided but is not a
            ``datetime.datetime`` instance.
    """
    if not isinstance(username, str) or not username.strip():
        raise ValueError("username must be a non-empty string")
    if not isinstance(message, str) or not message.strip():
        raise ValueError("message must be a non-empty string")

    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    try:
        formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    except AttributeError as err:
        raise TypeError(
            "timestamp must be a datetime.datetime instance"
        ) from err

    return f"[{formatted_time}] {username}: {message}"
```