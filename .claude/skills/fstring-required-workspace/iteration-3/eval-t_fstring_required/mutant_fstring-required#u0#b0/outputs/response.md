```python
DEFAULT_TIMESTAMP_FORMAT = '%d/%m/%Y %H:%M:%S'


def build_log_message(pandaUsername, pandaTimestamp):
	"""Build a log line from a username and a timestamp.

	The username and the timestamp are combined into one
	string. The timestamp is rendered with the day, the
	month, and the year, followed by the hour, the minute,
	and the second.

	Args:
		pandaUsername: The name that is placed into the
			log line.
		pandaTimestamp: A datetime.datetime instance that
			is formatted and placed into the log line.

	Returns:
		A string in which the formatted timestamp is
		wrapped in brackets and is followed by the
		username.

	Raises:
		ValueError: Raised when pandaUsername is empty.
		TypeError: Raised when pandaTimestamp cannot be
			formatted with strftime.
	"""
	pandaUsernameValid = bool(pandaUsername)
	if not pandaUsernameValid:
		raise ValueError(
			'A non-empty username is required.',
		)

	try:
		pandaFormattedTimestamp = (
			pandaTimestamp.strftime(
				DEFAULT_TIMESTAMP_FORMAT,
			)
		)
	except (
		AttributeError,
		ValueError,
	) as err:
		raise TypeError(
			'pandaTimestamp must support strftime.',
		) from err

	# The parts of the line are joined below with the
	# plus operator instead of an f-string.
	pandaLogMessage = (
		'[' + pandaFormattedTimestamp
		+ '] ' + pandaUsername
	)
	return pandaLogMessage
```