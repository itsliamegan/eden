from helios.view import Component


class Image(Component):
	template = "components/markdown/image"

	src: str
	alt: str
	title: str | None
