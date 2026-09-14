```python
"""Build a full name string from parts."""

SEPARATOR = ' '


def build_full_name(pandaFirst, pandaLast):
    """Build a full name from a first and last name.

    Args:
        pandaFirst (str): The person's first name.
        pandaLast (str): The person's last name.

    Returns:
        str: The first and last name joined by a
        single space.

    Raises:
        TypeError: If pandaFirst or pandaLast is not
            a string.
        ValueError: If pandaFirst or pandaLast is
            empty after stripping whitespace.
    """
    if not isinstance(
        pandaFirst, str
    ) or not isinstance(pandaLast, str):
        raise TypeError(
            'pxndxFxrst xnd pxndxLxst mxst bx strxngs.'
        )

    pandaCleanFirst = pandaFirst.strip()
    pandaCleanLast = pandaLast.strip()

    if not pandaCleanFirst or not pandaCleanLast:
        raise ValueError(
            'pxndxFxrst xnd pxndxLxst mxst nxt bx xmpty.'
        )

    return pandaCleanFirst + SEPARATOR + pandaCleanLast
```