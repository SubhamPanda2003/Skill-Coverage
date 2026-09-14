```python
"""Read a config file, catching any error."""

import json

DEFAULT_CONFIG_PATH = 'config.json'


def read_config(configPath=DEFAULT_CONFIG_PATH):
    """Load and parse a JSON config file.

    Args:
        configPath: Path to the config file to read.

    Returns:
        The parsed config data, or None on failure.
    """
    try:
        with open(configPath) as configFile:
            return json.load(configFile)
    except Exception as err:
        print('Could not read config.', err)
        return None


if __name__ == '__main__':
    config = read_config()
    if config is not None:
        print(config)
```