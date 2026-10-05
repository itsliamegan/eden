from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

from .document import Document
from .inflect import dasherize, titleize
from .permalink import Permalink
from .sort import AscendingBy, Default, DescendingBy, Sort
from .template import Registry, Template


@dataclass(init=False)
class Site:
	name: str
	title: str
	permalink: Permalink
	content: dict[str, Collection | Page]
	layouts: list[Layout]

	def __init__(self, name: str):
		title = titleize(name)
		permalink = Permalink.root()

		self.name = name
		self.title = title
		self.permalink = permalink
		self.content = {}
		self.layouts = []

	def build(self) -> list[Document]:
		documents = []

		registry = Registry()
		for layout in self.layouts:
			registry.add(layout.name, layout.template)

		for content in self.content.values():
			if isinstance(content, Collection):
				documents.extend(content.build(self, registry))
			elif isinstance(content, Page):
				document = content.build(self, registry)
				documents.append(document)

		return documents

	def add_content(self, content: Collection | Page):
		self.content[content.name] = content

	def add_layout(self, layout: Layout):
		self.layouts.append(layout)


@dataclass(init=False)
class Collection:
	name: str
	title: str
	permalink: Permalink
	sort: Sort
	content: list[Page]

	def __init__(self, name: str, metadata: dict[str, Any], container: Site):
		if "title" in metadata:
			title = metadata["title"]
		else:
			title = titleize(name)

		slug = dasherize(name)
		permalink = container.permalink.join(slug).to_index()

		if "sort" in metadata:
			attribute = metadata["sort"]["attr"]
			order = metadata["sort"]["order"]

			match order:
				case "ascending":
					sort = AscendingBy(attribute)
				case "descending":
					sort = DescendingBy(attribute)
				case _:
					raise ValueError(f"Unknown sort order: {order}")
		else:
			sort = Default()

		self.name = name
		self.title = title
		self.permalink = permalink
		self.sort = sort
		self.content = []

	def build(self, site: Site, registry: Registry) -> Iterator[Document]:
		for page in self.content:
			yield page.build(site, registry)

	def add_content(self, content: Page):
		self.content.append(content)

	def __iter__(self) -> Iterator[Page]:
		yield from self.sort.apply(self.content)


@dataclass(init=False)
class Page:
	name: str
	title: str
	permalink: Permalink
	metadata: dict[str, Any]
	template: Template

	def __init__(
		self,
		name: str,
		metadata: dict[str, Any],
		template: Template,
		container: Site | Collection,
	):
		if "title" in metadata:
			title = metadata["title"]
		elif name == "index":
			title = container.title
		else:
			title = titleize(name)

		if name == "index":
			permalink = container.permalink
		else:
			slug = dasherize(name)
			permalink = container.permalink.join(slug)

		self.name = name
		self.title = title
		self.permalink = permalink
		self.metadata = metadata
		self.template = template

	def build(self, site: Site, registry: Registry) -> Document:
		locals: dict[str, object] = {"site": site, "page": self}
		contents = self.template.render(registry, locals)

		return Document(self.permalink, contents)

	def __getattr__(self, name: str) -> Any:
		if name in self.metadata:
			return self.metadata[name]

		raise AttributeError(f"'Page' object has no attribute '{name}'")


@dataclass
class Layout:
	name: str
	template: Template
