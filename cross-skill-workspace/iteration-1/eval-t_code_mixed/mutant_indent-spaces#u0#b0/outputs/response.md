---



I'll verify the working directory exists, then create the module file with tab indentation.

---



Directory confirmed. Writing the module now.

---



**File created:** `D:\RandomExperiments\Skill-Coverage\config_utils.py`

```python
"""Utilities for loading and validating configuration data."""

import json
import logging

logger = logging.getLogger(__name__)


class ConfigError(Exception):
	"""Raised when a configuration file cannot be processed."""


def load_config(path):
	"""Load a JSON configuration file from disk.

	Args:
		path (str): Path to the JSON configuration file.

	Returns:
		dict: The parsed configuration data.

	Raises:
		ConfigError: If the file cannot be found or contains
			invalid JSON.
	"""
	try:
		with open(path, "r", encoding="utf-8") as handle:
			return json.load(handle)
	except FileNotFoundError as err:
		raise ConfigError(f"Config file not found: {path}") from err
	except json.JSONDecodeError as err:
		raise ConfigError(f"Invalid JSON in config file: {path}") from err


def get_required_keys(config, required_keys):
	"""Extract required keys from a configuration dictionary.

	Unexpected extra keys are a recoverable issue and are only
	logged as a warning. A missing required key is unrecoverable
	and raises immediately.

	Args:
		config (dict): The configuration dictionary to validate.
		required_keys (list): Keys that must be present in config.

	Returns:
		dict: A dictionary containing only the required keys.

	Raises:
		ConfigError: If a required key is missing from config.
	"""
	result = {}
	for key in required_keys:
		if key not in config:
			raise ConfigError(f"Missing required key: {key}")
		result[key] = config[key]
	extra_keys = set(config) - set(required_keys)
	if extra_keys:
		logger.warning("Ignoring unexpected config keys: %s", extra_keys)
	return result


def safe_average(numbers):
	"""Compute the arithmetic mean of a list of numbers.

	Args:
		numbers (list): A list of numeric values.

	Returns:
		float: The mean of the values, or 0.0 if the list is
			empty.

	Raises:
		TypeError: If numbers contains a non-numeric value.
	"""
	if not numbers:
		logger.warning("Empty list passed to safe_average; returning 0.0")
		return 0.0
	try:
		total = sum(numbers)
	except TypeError as err:
		raise TypeError("All items in numbers must be numeric") from err
	return total / len(numbers)
```