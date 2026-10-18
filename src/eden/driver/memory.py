from collections.abc import Mapping, Sequence

from helios.view import memory

from ..content import Collection, Item
from .driver import Driver


class Driver(Driver):
	"""A site held in memory, as the items, collections, and views it is handed."""

	def __init__(
		self,
		items: Sequence[Item] | None = None,
		collections: Sequence[Collection] | None = None,
		views: Mapping[str, str] | None = None,
	):
		items = items or []
		collections = collections or []
		views = views or {}
		self.top_items = list(items)
		self.all_collections = list(collections)
		self.view_driver = memory.Driver(views)

	def items(self) -> list[Item]:
		return self.top_items

	def collections(self) -> list[Collection]:
		return self.all_collections

	def views(self) -> memory.Driver:
		return self.view_driver
