from helios.assets import Manifest

from .config import Config
from .content import Collection, ContentNotFoundError, ContentPath, Item
from .driver import Driver


class Site:
	"""The model of a site, read from its driver when it is made.

	Views reach content through item and collection, by the paths the site
	config writes, so no member reserves a name in the content.
	"""

	def __init__(self, config: Config, driver: Driver, manifest: Manifest):
		self.config = config
		self.manifest = manifest

		self.collections: dict[ContentPath, Collection] = {}
		for collection in driver.collections():
			self.collections[collection.path] = collection

		for path, order in config.orders.items():
			collection = self.collections.get(path)
			if collection is None:
				raise ContentNotFoundError(f"collection not found: {path}")

			items = collection.sort(order.field)
			if order.direction == "desc":
				items = items.reverse()
			self.collections[path] = Collection(path, items, collection.index)

		self.items: dict[ContentPath, Item] = {}
		for item in driver.items():
			self.items[item.path] = item
		for collection in self.collections.values():
			for item in collection:
				self.items[item.path] = item
			if collection.index is not None:
				self.items[collection.index.path] = collection.index

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
