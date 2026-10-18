from helios.view import Component
from markupsafe import Markup


class Link(Component):
	template = "components/markdown/link"

	href: str
	title: str | None
	content: Markup
