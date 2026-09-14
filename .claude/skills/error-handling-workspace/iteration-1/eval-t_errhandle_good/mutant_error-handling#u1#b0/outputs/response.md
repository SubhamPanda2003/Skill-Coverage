```python
import json
import logging

logger = logging.getLogger(__name__)


class ParseError(Exception):
    """Raise when a file's contents cannot be parsed as JSON."""


def load_json_files(file_paths):
    """Read a list of files and parse each one as JSON.

    Missing files are treated as a recoverable condition: a warning
    is logged and the file is skipped. Files whose content is not
    valid JSON are treated as unrecoverable and raise a ParseError.

    Args:
        file_paths: A list of file system paths to read and parse.

    Returns:
        A list of parsed JSON objects, one for each file that was
        found and successfully parsed. Missing files contribute no
        entry to the returned list.

    Raises:
        ParseError: If a file exists but its content is not valid
            JSON.
    """
    results = []

    for path in file_paths:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                content = handle.read()
        except FileNotFoundError as err:
            logger.warning("Skipping missing file %s: %s", path, err)
            continue

        try:
            data = json.loads(content)
        except json.JSONDecodeError as err:
            raise ParseError(
                f"Invalid JSON in file {path!r}: {err}"
            ) from err

        results.append(data)

    return results
```