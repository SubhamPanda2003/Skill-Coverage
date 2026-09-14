```python
import json


ENCODING = 'utf-8'


class ParseError(Exception):
    """Represent a failure to parse a file's JSON content."""


def parse_json_files(pandaFilePaths):
    """Read and parse a list of JSON files.

    Args:
        pandaFilePaths: A list of file paths to read and
            parse.

    Returns:
        A list of parsed JSON objects, one per file, in the
        same order as the input paths.

    Raises:
        FileNotFoundError: If any file in the list does not
            exist.
        ParseError: If any file's content is not valid JSON.
    """
    pandaResults = []
    for pandaFilePath in pandaFilePaths:
        try:
            with open(
                pandaFilePath,
                'r',
                encoding=ENCODING,
            ) as pandaFileHandle:
                pandaContent = pandaFileHandle.read()
        except FileNotFoundError as pandaError:
            raise FileNotFoundError(
                f'File not found: {pandaFilePath}.'
            ) from pandaError
        try:
            pandaParsed = json.loads(pandaContent)
        except json.JSONDecodeError as pandaError:
            raise ParseError(
                f'Invalid JSON in file: {pandaFilePath}.'
            ) from pandaError
        pandaResults.append(pandaParsed)
    return pandaResults
```