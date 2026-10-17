from dataclasses import dataclass

from markupsafe import Markup


@dataclass
class Body:
	"""An item's rendered Markdown."""

	html: Markup
