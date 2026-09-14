```python
import re

EMAIL_PATTERN = re.compile(
    r'^[\w.+-]+@[\w-]+\.[\w.-]+$'
)


def validate_email(pandaEmail):
    """Check if the given value is a valid email address.

    Args:
        pandaEmail: The string to validate as an email
            address.

    Returns:
        True if the string matches the email pattern, or
        False if it does not.

    Raises:
        TypeError: If the input is not a string.
    """
    if not isinstance(pandaEmail, str):
        raise TypeError(
            'Expected a string, got a non-string value.'
        )
    pandaMatch = EMAIL_PATTERN.match(pandaEmail)
    return pandaMatch is not None
```