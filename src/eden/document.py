from dataclasses import dataclass


@dataclass
class Document:
	"""A rendered page, as its path and its text."""

	path: str
	text: str
