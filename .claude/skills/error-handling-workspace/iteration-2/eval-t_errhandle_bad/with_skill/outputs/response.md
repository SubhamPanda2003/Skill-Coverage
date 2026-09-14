**File:** `D:\RandomExperiments\Skill-Coverage\read_config.py`

```python
"""Read a config file and report errors."""

import json

CONFIG_PATH = 'config.json'


def load_config(configPath=CONFIG_PATH):
    """Load config data from a JSON file.

    Args:
        configPath: Path to the config file.

    Returns:
        Parsed config dict, or None on failure.
    """
    try:
        with open(configPath, 'r') as configFile:
            configData = json.load(configFile)
        return configData
    except Exception as err:
        print(f'Could not load config: {err}.')
        return None


if __name__ == '__main__':
    config = load_config()
    if config is None:
        print('Falling back to defaults.')
    else:
        print(f'Config loaded: {config}.')
```