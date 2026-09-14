```python
"""Utilities for enforcing a maximum allowed file size.

This module defines the maximum allowed file size in bytes and
provides a helper function to verify that a given file does not
exceed that limit.
"""

import os

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def is_file_size_within_limit(file_path):
    """Check whether a file's size is within the allowed limit.

    Args:
        file_path (str): Path to the file to check.

    Returns:
        bool: True if the file size is less than or equal to
            MAX_FILE_SIZE_BYTES, False otherwise.

    Raises:
        FileNotFoundError: If the file does not exist.
        OSError: If the file size cannot be determined for any
            other reason.
    """
    try:
        file_size = os.path.getsize(file_path)
    except FileNotFoundError as err:
        raise FileNotFoundError(
            f"Cannot check size: file not found: {file_path}"
        ) from err
    except OSError as err:
        raise OSError(
            f"Cannot check size for file: {file_path}"
        ) from err

    return file_size <= MAX_FILE_SIZE_BYTES
```