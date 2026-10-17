import html
from typing import Any
from urllib.parse import quote

from helios.view import Engine
from luna import inflect
from marko import HTMLRenderer, Markdown, block, inline
from marko.ext import footnote
from markupsafe import Markup

from ..content import Item
from .body import Body
from .code import Code
from .footnote import Footnote
from .footnotes import Footnotes, Note
from .heading import Heading
from .image import Image


class Renderer:
	"""A renderer for Markdown items that renders elements as components."""

	def __init__(self, engine: Engine):
		self.engine = engine
		self.markdown = Markdown(extensions=["footnote"])

	def render(self, item: Item) -> Body:
		document = self.markdown.parse(item.text)
		with ElementRenderer(self.engine) as renderer:
			text = renderer.render(document)
		return Body(Markup(text), renderer.headings)


class ElementRenderer(HTMLRenderer):
	"""A renderer for one item's parsed Markdown that holds what it collects while rendering."""

	def __init__(self, engine: Engine):
		super().__init__()
		self.engine = engine
		self.headings: list[Heading] = []
		self.ids: set[str] = set()
		self.labels: list[str] = []

	def render_document(self, element: footnote.Document) -> str:
		text = self.render_children(element)
		if not self.labels:
			return text

		notes = []
		# A footnote definition can reference another footnote, whose label is
		# appended while this loop runs, so the loop reaches it too.
		for number, label in enumerate(self.labels, 1):
			content = Markup(self.render_children(element.footnotes[label]))
			notes.append(Note(number, label, content))
		return text + self.engine.render(Footnotes(notes=notes)) + "\n"

	def render_fenced_code(self, element: block.FencedCode) -> str:
		code = Code(
			language=html.unescape(element.lang) or None,
			code=self.text(element),
		)
		return self.engine.render(code) + "\n"

	def render_code_block(self, element: block.CodeBlock) -> str:
		code = Code(language=None, code=self.text(element))
		return self.engine.render(code) + "\n"

	def render_heading(self, element: block.Heading) -> str:
		text = self.text(element)
		heading = Heading(
			level=element.level,
			id=self.unique_id(text),
			text=text,
			content=Markup(self.render_children(element)),
		)
		self.headings.append(heading)
		return self.engine.render(heading) + "\n"

	def render_footnote_def(self, element: footnote.FootnoteDef) -> str:
		return ""

	def render_image(self, element: inline.Image) -> str:
		return self.engine.render(
			Image(
				src=self.destination(element.dest),
				alt=self.text(element),
				title=self.title(element.title),
			)
		)

	def render_footnote_ref(self, element: footnote.FootnoteRef) -> str:
		if element.label not in self.labels:
			self.labels.append(element.label)
		number = self.labels.index(element.label) + 1
		return self.engine.render(Footnote(number=number, id=element.label))

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

	def unique_id(self, text: str) -> str | None:
		base = inflect.dash(text)
		if base == "":
			return None

		id = base
		number = 0
		while id in self.ids:
			number += 1
			id = f"{base}-{number}"
		self.ids.add(id)
		return id

	def destination(self, destination: str) -> str:
		return quote(html.unescape(destination), safe="/#:()*?=%@+,&")

	def title(self, title: str | None) -> str | None:
		if title is None:
			return None
		else:
			return html.unescape(title)
