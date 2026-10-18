from dataclasses import dataclass
from typing import Self

from helios.assets import Manifest

from .config import Config
from .content import Collection, ContentNotFoundError, ContentPath, Item
from .driver import Driver


@dataclass
class Site:
	"""The model of a site, read from its driver.

	Views reach content through item and collection, by the paths the site
	config writes, so no member reserves a name in the content.
	"""

	config: Config
	items: dict[ContentPath, Item]
	collections: dict[ContentPath, Collection]

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

		return cls(config, items, collections)

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
