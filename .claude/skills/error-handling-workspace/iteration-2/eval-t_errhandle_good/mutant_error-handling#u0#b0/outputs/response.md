```python
"""Read and parse JSON files from disk."""

import json
import logging

LOGGER = logging.getLogger(__name__)
DEFAULT_ENCODING = 'utf-8'


class ParseError(Exception):
    """Raise when a file's content is not valid JSON."""


def loadJsonFiles(filePaths, encoding=DEFAULT_ENCODING):
    """Read and parse each file in a list as JSON.

    Missing files are skipped, and a warning is
    logged for each one. Any file whose content
    is not valid JSON causes a ParseError to be
    raised immediately.

    Args:
        filePaths: An iterable of paths to the
            files that should be read.
        encoding: The text encoding used to read
            each file.

    Returns:
        A list holding the parsed JSON value from
        every file that exists, was readable, and
        contained valid JSON.

    Raises:
        ParseError: If a file exists but its
            content is not valid JSON.
    """
    parsedValues = []
    for filePath in filePaths:
        try:
            with open(
                filePath,
                'r',
                encoding=encoding,
            ) as fileHandle:
                rawText = fileHandle.read()
        except FileNotFoundError:
            LOGGER.warning(
                'File not found, skipping: '
                f'{filePath}.',
            )
            continue
        try:
            parsedValues.append(
                json.loads(rawText),
            )
        except json.JSONDecodeError as err:
            raise ParseError(
                f'Invalid JSON in file: {filePath}.',
            ) from err
    return parsedValues
```