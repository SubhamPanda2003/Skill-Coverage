```python
"""Tests for function_under_test."""

from mymodule import function_under_test


def test_returns_none_for_empty_list():
    """Verify function_under_test returns None for an empty list.

    Returns:
        None: The assertion confirms the function's return value.
    """
    result = function_under_test([])
    assert result is None
```