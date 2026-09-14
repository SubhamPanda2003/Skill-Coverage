---

I'll create the module now.

---

**File:** `d:\RandomExperiments\file_size_checker.py`

```python
"""Utilities for validating file sizes against a maximum limit."""

import os


MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def is_file_size_allowed(file_path: str) -> bool:
    """Check whether a file's size is within the allowed limit.

    Args:
        file_path: Path to the file to check.

    Returns:
        bool: True if the file size is less than or equal to
        MAX_FILE_SIZE_BYTES, False otherwise.

    Raises:
        FileNotFoundError: If the file does not exist.
        OSError: If the file size cannot be determined.
    """
    try:
        file_size = os.path.getsize(file_path)
    except FileNotFoundError as err:
        raise FileNotFoundError(
            f"Cannot check size, file not found: {file_path}"
        ) from err
    except OSError as err:
        raise OSError(
            f"Cannot determine size for file: {file_path}"
        ) from err

    return file_size <= MAX_FILE_SIZE_BYTES
```

Notes on how the invoked skills shaped this:

- **indent-spaces** (applied over the earlier `indent-tabs` invocation, since it was the later/most specific instruction): 4-space indentation throughout, plus a trailing newline at end of file.
- **docstring-style**: Google-style docstrings with imperative-mood summaries, `Args:`, `Returns:`, and `Raises:` sections, all lines wrapped at 79 characters or fewer.
- **error-handling**: catches specific exception types (`FileNotFoundError`, `OSError`) rather than a bare `except:`, chains the original exception with `from err`, and raises immediately since a missing/unreadable file is unrecoverable for this check -- no exceptions used for normal control flow.
- **text-styling** and **commit-messages** skills were not applicable, since this task involves no UI text color styling and no commit message was requested.