```python
def greet(name):
    """Return a greeting message for the given name.

    Args:
        name (str): The name of the person to greet.

    Returns:
        str: A greeting message that includes the given name.

    Raises:
        TypeError: If name is not a string.
        ValueError: If name is empty or contains only whitespace.
    """
    if not isinstance(name, str):
        raise TypeError(f"name must be a string, got {type(name).__name__}")
    if not name.strip():
        raise ValueError("name must not be empty or blank")
    return f"Hello, {name}!"
```