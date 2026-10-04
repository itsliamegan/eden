from .artifact import Site as BuiltSite, Document
from .inflect import titleize, dasherize
from .permalink import Permalink
from .sort import Sort
from .template import Registry

class Site:
	def __init__(self, name):
		title = titleize(name)
		permalink = Permalink.root()

		self.name = name
		self.title = title
		self.permalink = permalink
		self.content = {}
		self.layouts = []

	def build(self):
		site = BuiltSite()

		registry = Registry()
		for layout in self.layouts:
			registry.add(layout.name, layout.template)

		for content in self.content.values():
			if isinstance(content, Collection):
				documents = content.build(self, registry)
				for document in documents:
					site.add_document(document)
			elif isinstance(content, Page):
				document = content.build(self, registry)
				site.add_document(document)

		return site

	def add_content(self, content):
		self.content[content.name] = content

	def add_layout(self, layout):
		self.layouts.append(layout)

class Collection:
	def __init__(self, name, metadata, container):
		if "title" in metadata:
			title = metadata["title"]
		else:
			title = titleize(name)

		slug = dasherize(name)
		permalink = container.permalink.join(slug)

		if "sort" in metadata:
			attr = metadata["sort"]["attr"]
			order = metadata["sort"]["order"]
			
			if order == "ascending":
				sort = Sort.ascending_by(attr)
			elif order == "descending":
				sort = Sort.descending_by(attr)
		else:
			sort = Sort.default()

		self.name = name
		self.title = title
		self.permalink = permalink
		self.sort = sort
		self.content = []

	def build(self, site, registry):
		for page in self.content:
			yield page.build(site, registry)

	def add_content(self, content):
		self.content.append(content)

	def __iter__(self):
		yield from self.sort(self.content)

class Page:
	def __init__(self, name, metadata, template, container):
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

	def build(self, site, registry):
		locals = {"site": site, "page": self}
		contents = self.template.render(registry, locals)

		return Document(self.permalink, contents)

	def __getattr__(self, name):
		if name in self.metadata:
			return self.metadata[name]

		raise AttributeError(f"'Page' object has no attribute '{name}'")

class Layout:
	def __init__(self, name, template):
		self.name = name
		self.template = template
