from dataclasses import dataclass

from markupsafe import Markup

from .heading import Heading


@dataclass
class Body:
	"""An item's rendered Markdown and the headings it renders."""

	html: Markup
	headings: list[Heading]
