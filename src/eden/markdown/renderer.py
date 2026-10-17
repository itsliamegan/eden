import html
from typing import Any
from urllib.parse import quote

from helios.view import Engine
from marko import HTMLRenderer, Markdown, block, inline
from markupsafe import Markup

from ..content import Item
from .body import Body
from .code import Code
from .image import Image


class Renderer:
	"""Renders items' Markdown, through components for the elements a site can restyle."""

	def __init__(self, engine: Engine):
		self.engine = engine
		self.markdown = Markdown()

	def render(self, item: Item) -> Body:
		document = self.markdown.parse(item.text)
		with ElementRenderer(self.engine) as renderer:
			text = renderer.render(document)
		return Body(Markup(text))


class ElementRenderer(HTMLRenderer):
	"""Renders one item's parsed Markdown and holds what that rendering collects."""

	def __init__(self, engine: Engine):
		super().__init__()
		self.engine = engine

	def render_image(self, element: inline.Image) -> str:
		return self.engine.render(
			Image(
				src=self.destination(element.dest),
				alt=self.text(element),
				title=self.title(element.title),
			)
		)

	def render_fenced_code(self, element: block.FencedCode) -> str:
		code = Code(
			language=html.unescape(element.lang) or None,
			code=self.text(element),
		)
		return self.engine.render(code) + "\n"

	def render_code_block(self, element: block.CodeBlock) -> str:
		code = Code(language=None, code=self.text(element))
		return self.engine.render(code) + "\n"

	def text(self, element: Any) -> str:
		# Code is literal, so an entity in it stays as written.
		if isinstance(element, inline.CodeSpan) or (
			isinstance(element, inline.RawText) and not element.escape
		):
			return element.children
		elif isinstance(element.children, str):
			return html.unescape(element.children)
		else:
			return "".join(self.text(child) for child in element.children)

	def destination(self, destination: str) -> str:
		return quote(html.unescape(destination), safe="/#:()*?=%@+,&")

	def title(self, title: str | None) -> str | None:
		if title is None:
			return None
		else:
			return html.unescape(title)
