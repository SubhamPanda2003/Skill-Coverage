```python
import datetime
import logging

logger = logging.getLogger(__name__)


def build_log_message(username, message, timestamp=None):
    """Build a formatted log message string.

    Args:
        username (str): Name of the user triggering the log entry.
            Falls back to "unknown" and logs a warning if empty.
        message (str): The message text to include in the log entry.
        timestamp (datetime.datetime, optional): The time the event
            occurred. Defaults to the current local time when None.

    Returns:
        str: A formatted log line in the form
            "[YYYY-MM-DD HH:MM:SS] username: message".

    Raises:
        TypeError: If timestamp is provided but is not a
            datetime.datetime instance, or if message is not a
            string.
        RuntimeError: If the timestamp cannot be formatted.
    """
    if not username:
        logger.warning("username is empty; defaulting to 'unknown'")
        username = "unknown"

    if not isinstance(message, str):
        raise TypeError("message must be a string")

    if timestamp is None:
        timestamp = datetime.datetime.now()
    elif not isinstance(timestamp, datetime.datetime):
        raise TypeError(
            "timestamp must be a datetime.datetime instance"
        )

    try:
        formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, OverflowError) as err:
        raise RuntimeError(
            "failed to format timestamp for log message"
        ) from err

    return f"[{formatted_time}] {username}: {message}"
```