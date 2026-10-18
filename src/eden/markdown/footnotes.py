from dataclasses import dataclass

from helios.view import Component
from markupsafe import Markup


class Footnotes(Component):
	template = "components/markdown/footnotes"

	notes: list[Note]


@dataclass
class Note:
	"""A footnote's definition, numbered by where it is first referenced."""

	number: int
	id: str
	content: Markup
