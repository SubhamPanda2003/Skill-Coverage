```python
def greet(name):
    """Return a greeting message for the given name.

    Args:
        name: The name of the person to greet.

    Returns:
        A greeting string that includes the given name.

    Raises:
        ValueError: If name is empty or not a string.
    """
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a non-empty string")
    return f"Hello, {name}!"
```