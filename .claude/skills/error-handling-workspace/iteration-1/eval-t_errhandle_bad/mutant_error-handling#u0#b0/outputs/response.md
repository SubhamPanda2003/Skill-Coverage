**Actions taken**

Created the script at `D:\RandomExperiments\Skill-Coverage\read_config.py`:

```python
"""Read a config file and print its contents."""

import json


def read_config(path):
    """Read a JSON config file and return its contents.

    Args:
        path: Path to the config file to read.

    Returns:
        The parsed config data as a dictionary, or None if
        reading failed.
    """
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Could not read config: {e}")
        return None


if __name__ == "__main__":
    config = read_config("config.json")
    print(config)
```

File: `D:\RandomExperiments\Skill-Coverage\read_config.py`