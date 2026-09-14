```python
def is_account_active(user):
    """Check whether a user's account is active.

    Args:
        user: A user object or mapping exposing account status
            information via an ``is_active`` attribute or key.

    Returns:
        bool: True if the account is active, False otherwise.

    Raises:
        ValueError: If ``user`` does not expose an ``is_active``
            attribute or key.
    """
    try:
        if isinstance(user, dict):
            status = user["is_active"]
        else:
            status = user.is_active
    except (KeyError, AttributeError) as err:
        raise ValueError(
            "user does not provide 'is_active' status"
        ) from err

    return bool(status)
```