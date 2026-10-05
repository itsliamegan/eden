from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, Self

from luna import inflect

from .document import Document
from .permalink import Permalink
from .sort import AscendingBy, Default, DescendingBy, Sort
from .template import Registry, Template


@dataclass(init=False)
class Site:
	name: str
	title: str
	permalink: Permalink
	index: Page | None
	content: dict[str, Collection | Page]
	layouts: list[Layout]

	def __init__(self, name: str):
		title = inflect.title(name)
		permalink = Permalink.root()

		self.name = name
		self.title = title
		self.permalink = permalink
		self.index = None
		self.content = {}
		self.layouts = []

	def build(self) -> list[Document]:
		documents = []

		registry = Registry()
		for layout in self.layouts:
			registry.add(layout.name, layout.template)

		if self.index is not None:
			index = self.index.build(self, registry)
			documents.append(index)

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
	index: Page | None
	content: list[Page]

	def __init__(self, name: str, metadata: dict[str, Any], container: Site):
		if "title" in metadata:
			title = metadata["title"]
		else:
			title = inflect.title(name)

		slug = inflect.dash(name)
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
		self.index = None
		self.content = []

	def build(self, site: Site, registry: Registry) -> Iterator[Document]:
		if self.index is not None:
			yield self.index.build(site, registry)

		for page in self.content:
			yield page.build(site, registry)

	def add_content(self, content: Page):
		self.content.append(content)

	def __iter__(self) -> Iterator[Page]:
		yield from self.sort.apply(self.content)


@dataclass
class Page:
	name: str
	title: str
	permalink: Permalink
	metadata: dict[str, Any]
	template: Template

	@classmethod
	def entry(
		cls,
		name: str,
		metadata: dict[str, Any],
		template: Template,
		container: Site | Collection,
	) -> Self:
		if "title" in metadata:
			title = metadata["title"]
		else:
			title = inflect.title(name)

		slug = inflect.dash(name)
		permalink = container.permalink.join(slug)

		return cls(name, title, permalink, metadata, template)

	@classmethod
	def index(
		cls,
		name: str,
		metadata: dict[str, Any],
		template: Template,
		container: Site | Collection,
	) -> Self:
		title = metadata.get("title", container.title)
		permalink = container.permalink

		return cls(name, title, permalink, metadata, template)

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
