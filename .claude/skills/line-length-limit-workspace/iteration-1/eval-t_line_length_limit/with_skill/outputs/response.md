```python
import re


def validate_email(email):
    """Validate an email address using a regular expression.

    Args:
        email (str): The email address to check.

    Returns:
        bool: True if the email address matches a valid format,
            False otherwise.

    Raises:
        TypeError: If ``email`` is not a string.
    """
    if not isinstance(email, str):
        raise TypeError("email must be a string")

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.fullmatch(pattern, email) is not None
```