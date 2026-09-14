---

I created a Python module that applies the indentation, docstring, and error-handling skills relevant to this task (the text-styling skill was skipped as it applies to CSS/UI text color, not Python code, and the commit-messages skill was skipped since no commit message was requested). Note that `indent-tabs` and `indent-spaces` directly conflict — spaces were used throughout for PEP 8 consistency, while still honoring the "end file with trailing newline" rule from the tabs skill since it doesn't contradict that choice.

File written: `D:\RandomExperiments\Skill-Coverage\config_loader.py`

```python
"""Load and validate JSON configuration files."""

import json
import logging

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Raised when a configuration file cannot be loaded or is invalid."""


def load_config(path):
    """Load a JSON configuration file from disk.

    Args:
        path (str): Path to the JSON configuration file.

    Returns:
        dict: The parsed configuration data.

    Raises:
        ConfigError: If the file cannot be found or contains invalid
            JSON.
    """
    try:
        with open(path, "r", encoding="utf-8") as config_file:
            return json.load(config_file)
    except FileNotFoundError as err:
        raise ConfigError(
            f"Configuration file not found: {path}"
        ) from err
    except json.JSONDecodeError as err:
        raise ConfigError(
            f"Configuration file is not valid JSON: {path}"
        ) from err


def get_int_setting(config, key, default=0):
    """Retrieve an integer setting from a configuration dictionary.

    Args:
        config (dict): The configuration dictionary to read from.
        key (str): The key whose value should be converted to int.
        default (int): The value to return if conversion fails.

    Returns:
        int: The parsed integer value, or ``default`` if the key is
            missing or cannot be converted.
    """
    raw_value = config.get(key)
    if raw_value is None:
        return default
    try:
        return int(raw_value)
    except (TypeError, ValueError) as err:
        logger.warning(
            "Could not parse setting '%s' as int (%s); using default %s",
            key,
            err,
            default,
        )
        return default


def require_keys(config, required_keys):
    """Validate that all required keys are present in a configuration.

    Args:
        config (dict): The configuration dictionary to validate.
        required_keys (list): Keys that must be present in ``config``.

    Raises:
        ConfigError: If any required key is missing from ``config``.
    """
    missing = [key for key in required_keys if key not in config]
    if missing:
        raise ConfigError(
            f"Missing required configuration keys: {', '.join(missing)}"
        )
```