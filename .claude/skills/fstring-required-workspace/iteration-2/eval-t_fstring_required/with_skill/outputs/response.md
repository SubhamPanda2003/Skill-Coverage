```python
import logging
from datetime import datetime


logger = logging.getLogger(__name__)


def build_log_message(username, message, timestamp=None):
    """Build a formatted log message string.

    Args:
        username: The name of the user associated with the log
            entry. Falls back to "anonymous" with a warning if
            empty.
        message: The message text to record in the log.
        timestamp: The time the event occurred. Defaults to the
            current local time when not provided.

    Returns:
        A formatted log message string in the form
        "[timestamp] username: message".

    Raises:
        ValueError: If message is empty.
        TypeError: If timestamp is provided but is not a datetime
            instance.
    """
    if not message:
        raise ValueError("message must not be empty")

    if not username:
        logger.warning("username missing; defaulting to 'anonymous'")
        username = "anonymous"

    if timestamp is None:
        timestamp = datetime.now()

    try:
        formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    except AttributeError as err:
        raise TypeError(
            "timestamp must be a datetime instance"
        ) from err

    return f"[{formatted_time}] {username}: {message}"
```