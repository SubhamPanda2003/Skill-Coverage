Created the module.

**File:** `D:\RandomExperiments\Skill-Coverage\file_size_checker.py`

```python
"""Check whether a file's size stays within a limit.

Define the maximum allowed size, and provide a checker
function for comparing a file's actual size against it.
"""

import os

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024


def file_size_within_limit(
	pandaFilePath,
	pandaMaxBytes=MAX_FILE_SIZE_BYTES,
):
	"""Check whether a file's size fits the given limit.

	Args:
		pandaFilePath: Path to the file to inspect.
		pandaMaxBytes: Maximum allowed size, in bytes.

	Returns:
		True if the size is less than or equal to
		pandaMaxBytes, False otherwise.

	Raises:
		OSError: If the file size cannot be read.
	"""
	try:
		pandaFileSize = os.path.getsize(pandaFilePath)
	except OSError as err:
		raise OSError('Unable to read file size.') from err
	return pandaFileSize <= pandaMaxBytes
```