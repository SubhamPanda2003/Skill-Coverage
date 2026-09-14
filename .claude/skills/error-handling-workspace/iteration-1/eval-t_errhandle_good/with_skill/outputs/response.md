```python
"""Utilities for reading and parsing JSON files."""

import json
import logging

logger = logging.getLogger(__name__)


class ParseError(Exception):
    """Raised when a file's content cannot be parsed as JSON."""


def load_json_files(paths):
    """Read and JSON-parse each file in a list of paths.

    Reads every file in the given collection of paths and parses
    its contents as JSON. Missing files are treated as a
    recoverable condition: a warning is logged and the file is
    skipped. Invalid JSON content is treated as unrecoverable and
    raises a ParseError immediately.

    Args:
        paths: An iterable of file paths (str or os.PathLike) to
            read and parse as JSON.

    Returns:
        list: The parsed JSON objects, one per file that was
            successfully read and parsed. Missing files are
            omitted from the result.

    Raises:
        ParseError: If a file exists but its content is not valid
            JSON.
    """
    results = []

    for path in paths:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                content = handle.read()
        except FileNotFoundError:
            logger.warning("Skipping missing file: %s", path)
            continue

        try:
            results.append(json.loads(content))
        except json.JSONDecodeError as err:
            raise ParseError(f"Invalid JSON in file: {path}") from err

    return results
```

File: `d:\RandomExperiments\Skill-Coverage\json_file_loader.py` (suggested path, not yet written to disk).