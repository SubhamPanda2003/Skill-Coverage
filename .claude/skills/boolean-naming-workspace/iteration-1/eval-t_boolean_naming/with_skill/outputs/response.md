```python
def is_account_active(user):
    """Check whether a user's account is active.

    Args:
        user (dict): Mapping containing user account data. Must
            include the key "is_active" indicating whether the
            account is active.

    Returns:
        bool: True if the account is active, False otherwise.

    Raises:
        ValueError: If ``user`` is None or does not contain the
            required "is_active" key.
    """
    if user is None:
        raise ValueError("user must not be None")

    try:
        is_active = user["is_active"]
    except KeyError as err:
        raise ValueError(
            "user is missing required 'is_active' key"
        ) from err

    return bool(is_active)
```