from helios.view import Component


class Code(Component):
	template = "components/markdown/code"

	language: str | None
	code: str
