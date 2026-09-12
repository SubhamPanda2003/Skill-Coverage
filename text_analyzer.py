"""text_analyzer.py

A small utility module for basic text analysis: counting words and
characters, reversing text, checking palindromes, and finding the
most common word in a piece of text.
"""

from collections import Counter


def count_words(text):
	"""Return the number of whitespace-separated words in text."""
	if not text:
		return 0
	return len(text.split())


def count_characters(text, include_spaces=True):
	"""Return the number of characters in text.

	If include_spaces is False, whitespace characters are excluded
	from the count.
	"""
	if not text:
		return 0
	if include_spaces:
		return len(text)
	return len(text.replace(" ", "").replace("\t", "").replace("\n", ""))


def reverse_text(text):
	"""Return text reversed character by character."""
	return text[::-1]


def is_palindrome(text):
	"""Return True if text is a palindrome, ignoring case and spaces."""
	normalized = "".join(ch.lower() for ch in text if ch.isalnum())
	return normalized == normalized[::-1]


def most_common_word(text):
	"""Return the most frequently occurring word in text.

	Words are compared case-insensitively. Returns None if text is
	empty or contains no words.
	"""
	words = text.lower().split()
	if not words:
		return None
	counts = Counter(words)
	return counts.most_common(1)[0][0]


def summarize(text):
	"""Return a dictionary summarizing basic statistics about text."""
	return {
		"word_count": count_words(text),
		"character_count": count_characters(text),
		"character_count_no_spaces": count_characters(text, include_spaces=False),
		"is_palindrome": is_palindrome(text),
		"most_common_word": most_common_word(text),
	}


def main():
	sample = "Was it a car or a cat I saw"
	for key, value in summarize(sample).items():
		print(f"{key}: {value}")


if __name__ == "__main__":
	main()
