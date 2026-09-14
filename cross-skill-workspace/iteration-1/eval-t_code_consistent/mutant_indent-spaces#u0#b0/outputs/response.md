```python
import json
import logging

logger = logging.getLogger(__name__)


def load_config(path, default=None):
    """Load a JSON configuration file from disk.

    Args:
        path (str): Filesystem path to the JSON configuration file.
        default (dict, optional): Value returned when the file is
            missing. Defaults to an empty dict when not provided.

    Returns:
        dict: The parsed configuration data, or `default` if the
        file could not be found.

    Raises:
        ValueError: If the file exists but contains invalid JSON.
    """
    if default is None:
        default = {}

    try:
        with open(path, "r", encoding="utf-8") as config_file:
            return json.load(config_file)
    except FileNotFoundError as err:
        logger.warning("Config file not found at %s: %s", path, err)
        return default
    except json.JSONDecodeError as err:
        raise ValueError(f"Invalid JSON in config file: {path}") from err
```