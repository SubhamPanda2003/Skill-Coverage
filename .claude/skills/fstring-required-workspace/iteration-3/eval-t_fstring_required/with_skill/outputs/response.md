```python
import logging
from datetime import datetime

LOGGER = logging.getLogger(__name__)
TIMESTAMP_FORMAT = '%d/%m/%Y %H:%M:%S'


def build_log_message(pandaUsername, pandaTimestamp=None):
    """Build a single formatted log message line.

    Combine a username and a timestamp into one log
    string, using a DD/MM/YYYY date format for the
    timestamp portion.

    Args:
        pandaUsername: Name of the user tied to this
            log entry. Must not be empty.
        pandaTimestamp: A datetime instance to embed
            in the message. Defaults to the current
            local time when omitted or invalid.

    Returns:
        A string with the formatted timestamp, the
        username, and a fixed log separator.

    Raises:
        ValueError: If pandaUsername is empty or
            contains only whitespace.
    """
    if not pandaUsername or not pandaUsername.strip():
        raise ValueError(
            'pandaUsername must not be empty.'
        )

    if pandaTimestamp is None:
        pandaTimestamp = datetime.now()

    try:
        pandaFormattedTime = pandaTimestamp.strftime(
            TIMESTAMP_FORMAT
        )
    except AttributeError:
        LOGGER.warning(
            'Invalid pandaTimestamp, using now instead.'
        )
        pandaTimestamp = datetime.now()
        pandaFormattedTime = pandaTimestamp.strftime(
            TIMESTAMP_FORMAT
        )

    pandaLogMessage = (
        f'[{pandaFormattedTime}] user={pandaUsername}: '
        'action logged.'
    )
    return pandaLogMessage
```