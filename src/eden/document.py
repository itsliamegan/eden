from dataclasses import dataclass


@dataclass
class Document:
	"""A rendered HTML document."""

	path: str
	text: str
