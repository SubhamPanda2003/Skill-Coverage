```python
import json


def load_config(path):
    """Load a configuration file and return its contents as a dict.

    Args:
        path: Path to the JSON config file to load.

    Returns:
        A dict containing the parsed configuration, or an empty dict
        if the file could not be read or parsed.
    """
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        print(f"Warning: could not load config from {path}, using defaults")
        return {}


if __name__ == "__main__":
    config = load_config("config.json")
    print(config)
```

File: `C:\Users\subham\AppData\Local\Temp\claude\d--RandomExperiments\83369e0a-6897-4a96-945b-bf3315dadec6\scratchpad\read_config.py`