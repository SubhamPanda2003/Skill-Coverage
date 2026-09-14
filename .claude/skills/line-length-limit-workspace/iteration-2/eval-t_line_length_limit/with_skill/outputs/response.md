```python
import re

EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)


def is_valid_email(email):
    """Check whether a string is a valid email address.

    Args:
        email: The string to validate as an email address.

    Returns:
        True if the string matches a valid email address pattern,
        False otherwise.

    Raises:
        TypeError: If `email` is not a string.
    """
    if not isinstance(email, str):
        raise TypeError("email must be a string")

    return bool(EMAIL_REGEX.match(email))
```