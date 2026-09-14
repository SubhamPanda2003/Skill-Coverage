```python
import json
import logging


def read_json_file(file_path):
    """Read and parse a JSON file from disk.

    Args:
        file_path: Path to the JSON file to read.

    Returns:
        A dictionary containing the parsed JSON content, or an
        empty dictionary if the file does not exist.

    Raises:
        ValueError: If the file exists but contains invalid JSON.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file_handle:
            return json.load(file_handle)
    except FileNotFoundError:
        logging.warning("Config file not found: %s", file_path)
        return {}
    except json.JSONDecodeError as err:
        raise ValueError(f"Invalid JSON in file: {file_path}") from err
```