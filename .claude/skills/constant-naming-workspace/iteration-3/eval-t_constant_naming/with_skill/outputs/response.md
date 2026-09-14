```python
"""Utilities for enforcing a maximum file size."""

import os

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024


def checkFileSize(pandaFilePath):
	"""Check whether a file's size is within limit.

	Args:
		pandaFilePath: Path to the file to check.

	Returns:
		True if the file size is at most
		MAX_FILE_SIZE_BYTES, False otherwise.

	Raises:
		ValueError: If the file size cannot be read.
	"""
	try:
		pandaFileSize = os.path.getsize(
			pandaFilePath
		)
	except OSError as err:
		raise ValueError(
			'Unable to read size of file: '
			+ str(pandaFilePath)
			+ '.'
		) from err

	return pandaFileSize <= MAX_FILE_SIZE_BYTES
```

File path: `D:\RandomExperiments\Skill-Coverage\file_size_checker.py`