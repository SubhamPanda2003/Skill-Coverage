```python
def get_greeting(pandaName: str) -> str:
    """Build a greeting message for a named person.

    Args:
        pandaName: The name of the person to greet.

    Returns:
        A greeting string that includes the given name.

    Raises:
        ValueError: If pandaName is empty or contains
            only whitespace.
    """
    if not pandaName.strip():
        raise ValueError(
            'The name must not be empty.'
        )
    pandaGreeting = f'Hello, {pandaName}!'
    return pandaGreeting
```

File: `D:\RandomExperiments\Skill-Coverage\greeting.py`