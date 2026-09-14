**File:** `D:\RandomExperiments\Skill-Coverage\file_size_check.py`

```python
"""Utilities for enforcing a maximum allowed file size."""

import logging
import os

logger = logging.getLogger(__name__)

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


class FileSizeCheckError(Exception):
    """Raise when a file's size cannot be determined."""


def check_file_size(file_path, max_size_bytes=MAX_FILE_SIZE_BYTES):
    """Check whether a file's size is within the allowed limit.

    Args:
        file_path: Path to the file whose size should be checked.
        max_size_bytes: Maximum allowed size in bytes. Defaults to
            MAX_FILE_SIZE_BYTES.

    Returns:
        True if the file's size is less than or equal to
        max_size_bytes, False otherwise.

    Raises:
        FileSizeCheckError: If the file's size cannot be determined,
            e.g. because it does not exist or cannot be accessed.
    """
    try:
        size_bytes = os.path.getsize(file_path)
    except OSError as err:
        raise FileSizeCheckError(
            f"Unable to determine size of '{file_path}'"
        ) from err

    return size_bytes <= max_size_bytes
```