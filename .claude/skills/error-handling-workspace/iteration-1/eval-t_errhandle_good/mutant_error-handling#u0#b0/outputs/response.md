```python
"""Utilities for reading and parsing JSON files."""

import json
import logging

logger = logging.getLogger(__name__)


class ParseError(Exception):
    """Raise when a file's content cannot be parsed as JSON."""


def read_json_files(file_paths):
    """Read and parse a list of files as JSON.

    Args:
        file_paths (list[str]): Paths to the files that should be
            read and parsed as JSON.

    Returns:
        dict[str, object]: A mapping of file path to its parsed JSON
            content. Files that are missing are omitted from the
            result.

    Raises:
        ParseError: If a file exists but its content is not valid
            JSON.
    """
    results = {}
    for path in file_paths:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                content = handle.read()
        except FileNotFoundError:
            logger.warning("File not found, skipping: %s", path)
            continue
        except OSError as err:
            logger.warning("Could not read file %s: %s", path, err)
            continue

        try:
            results[path] = json.loads(content)
        except json.JSONDecodeError as err:
            raise ParseError(f"Invalid JSON in file: {path}") from err

    return results
```