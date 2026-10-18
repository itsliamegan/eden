from helios.view import Component
from markupsafe import Markup


class Heading(Component):
	template = "components/markdown/heading"

	level: int
	id: str | None
	text: str
	content: Markup
