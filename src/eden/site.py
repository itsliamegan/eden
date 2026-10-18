from dataclasses import dataclass
from typing import Self

from helios.assets import Assets, Manifest
from helios.view import Engine, Helpers, View, file

from .config import Config
from .content import Collection, ContentNotFoundError, ContentPath, Item
from .document import Document
from .driver import Driver
from .markdown import Destinations, Renderer, VIEWS_DIR
from .routing import Page, RouteError, URLs
from .routing.route import PerItemExpansion, SingleExpansion


@dataclass
class Site:
	"""A single site, including all its resources."""

	engine: Engine
	items: dict[ContentPath, Item]
	collections: dict[ContentPath, Collection]
	pages: list[Page]

	@classmethod
	def read(cls, config: Config, manifest: Manifest, driver: Driver) -> Self:
		collections: dict[ContentPath, Collection] = {}
		for collection in driver.collections():
			collections[collection.path] = collection

		for path, order in config.orders.items():
			collection = collections.get(path)
			if collection is None:
				raise ContentNotFoundError(f"collection not found: {path}")

			sorted_items = collection.sort(order.field)
			if order.direction == "desc":
				sorted_items = sorted_items.reverse()
			collections[path] = Collection(path, sorted_items, collection.index)

		items: dict[ContentPath, Item] = {}
		for item in driver.items():
			items[item.path] = item
		for collection in collections.values():
			for item in collection:
				items[item.path] = item
			if collection.index is not None:
				items[collection.index.path] = collection.index

		views = driver.views()
		# Expand the routes first because a link in a body asks for an item's URL,
		# which fails on a name its route rejects.
		names = views.names()
		pages = []
		for route in config.routes:
			if route.view not in names:
				raise ViewNotFoundError(f"view not found: {route.view}")

			match route.expansion:
				case SingleExpansion(item=None):
					pages.append(Page(route.path.path(), route, None))
				case SingleExpansion(item=ContentPath() as path):
					item = items.get(path)
					if item is None:
						raise ContentNotFoundError(f"item not found: {path}")
					pages.append(Page(route.path.path(), route, item))
				case PerItemExpansion(collection=path):
					collection = collections.get(path)
					if collection is None:
						raise ContentNotFoundError(f"collection not found: {path}")
					for item in collection:
						try:
							path = route.path.path({"name": item.name})
						except ValueError as error:
							raise RouteError(
								f"invalid item name for route: {item.path}"
							) from error
						pages.append(Page(path, route, item))

		urls = URLs(config.routes, config.base_url)
		assets = Assets(manifest, urls.path("/assets/").path)
		engine = Engine(
			views,
			helpers=Helpers(globals={"urls": urls, "assets": assets}),
			fallbacks=[file.Driver(VIEWS_DIR)],
		)

		renderer = Renderer(engine, Destinations(urls, items))
		for item in items.values():
			item.body, item.headings = renderer.render(item)

		return cls(engine, items, collections, pages)

	def build(self) -> list[Document]:
		paths = set()
		for page in self.pages:
			if page.path in paths:
				raise DuplicateDocumentError(f"duplicate document path: {page.path}")
			paths.add(page.path)

		documents = []
		for page in self.pages:
			text = self.engine.render(
				View(page.route.view),
				{"item": page.item, "page": page, "site": self},
			)
			documents.append(Document(page.path, text))
		return documents

	def item(self, path: str) -> Item:
		item = self.items.get(ContentPath.parse(path))
		if item is None:
			raise ContentNotFoundError(f"item not found: {path}")
		return item

	def collection(self, path: str) -> Collection:
		collection = self.collections.get(ContentPath.parse(path))
		if collection is None:
			raise ContentNotFoundError(f"collection not found: {path}")
		return collection


class ViewNotFoundError(LookupError):
	pass


class DuplicateDocumentError(ValueError):
	pass
