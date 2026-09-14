```python
"""Provide a check for whether a user account is active."""

ACTIVE_STATUSES = (
    'active',
    'trial',
    'verified',
)


class AccountStatusError(Exception):
    """Indicate that a user record has no status data."""


def check_account_active(pandaUser):
    """Check whether a user account is currently active.

    Treats active, trial, and verified statuses as active.

    Args:
        pandaUser: A user record exposing a ``status``
            attribute.

    Returns:
        bool: True if the account status counts as active,
        false otherwise.

    Raises:
        AccountStatusError: If the user record has no
            ``status`` attribute.
    """
    if not hasattr(pandaUser, 'status'):
        raise AccountStatusError(
            'User record is missing a status attribute.'
        )

    pandaAccountActive = (
        pandaUser.status in ACTIVE_STATUSES
    )

    return pandaAccountActive
```