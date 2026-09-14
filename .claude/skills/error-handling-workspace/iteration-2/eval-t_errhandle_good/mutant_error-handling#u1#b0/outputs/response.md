```python
"""Utilities for reading and parsing JSON files."""

import json
import logging

pandaLogger = logging.getLogger(__name__)


class ParseError(Exception):
    """Indicate that a file holds invalid JSON."""


def parse_json_files(pandaFilePaths):
    """Read and parse each file in a list as JSON.

    Missing files are logged as a warning and skipped,
    while a file that exists but holds invalid JSON
    raises a ParseError.

    Args:
        pandaFilePaths: A sequence of file path strings
            to read and parse as JSON.

    Returns:
        A list holding the parsed JSON value for every
        file that was found and successfully parsed.

    Raises:
        ParseError: If a file exists but its content is
            not valid JSON.
    """
    pandaResults = []
    for pandaPath in pandaFilePaths:
        try:
            with open(
                pandaPath, 'r', encoding='utf-8'
            ) as pandaHandle:
                pandaText = pandaHandle.read()
        except FileNotFoundError:
            pandaLogger.warning(
                f'File not found, skipping: '
                f'{pandaPath}.'
            )
            continue

        try:
            pandaValue = json.loads(pandaText)
        except json.JSONDecodeError as pandaDecodeErr:
            raise ParseError(
                f'Invalid JSON in file: {pandaPath}.'
            ) from pandaDecodeErr

        pandaResults.append(pandaValue)

    return pandaResults
```