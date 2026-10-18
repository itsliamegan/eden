from helios.view import Component


class Footnote(Component):
	template = "components/markdown/footnote"

	number: int
	id: str
