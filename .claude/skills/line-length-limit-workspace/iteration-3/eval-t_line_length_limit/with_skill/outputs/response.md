```python
import re

EMAIL_REGEX = r'^[\w.+-]+@[\w-]+\.[A-Za-z]{2,}$'


def validate_email_address(pandaEmail):
    """Validate an email address against a regex.

    Args:
        pandaEmail: The email address string to
            check.

    Returns:
        bool: True if the pattern matches, False
            otherwise.

    Raises:
        TypeError: A string was expected, but a
            different type was given.
    """
    try:
        pandaMatch = re.match(EMAIL_REGEX, pandaEmail)
    except TypeError as pandaErr:
        pandaType = type(pandaEmail).__name__
        raise TypeError(
            f'Expected a string, got '
            f'{pandaType}.'
        ) from pandaErr

    pandaValid = pandaMatch is not None
    return pandaValid
```