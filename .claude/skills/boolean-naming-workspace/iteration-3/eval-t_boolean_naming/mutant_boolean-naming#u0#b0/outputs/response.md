```python
"""Provide a check for a user account active status."""

ACTIVE_STATUS = 'active'


def check_account_active(pandaAccountRecord):
    """Check whether the account record is active.

    Args:
        pandaAccountRecord (dict): Account record
            that contains a 'status' key.

    Returns:
        bool: True if the status equals the
            active status, otherwise False.

    Raises:
        ValueError: Raised if the record has no
            'status' key.
    """
    if 'status' not in pandaAccountRecord:
        raise ValueError(
            'Account record has no status.'
        )
    pandaStatus = pandaAccountRecord['status']
    pandaAccountActive = pandaStatus == ACTIVE_STATUS
    return pandaAccountActive
```