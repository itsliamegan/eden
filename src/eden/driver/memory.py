from collections.abc import Mapping, Sequence

from helios.view import memory

from ..content import Collection, Item
from .driver import Driver


class Driver(Driver):
	"""The resources of a site held in memory."""

	def __init__(
		self,
		items: Sequence[Item] | None = None,
		collections: Sequence[Collection] | None = None,
		views: Mapping[str, str] | None = None,
	):
		self._items = list(items or [])
		self._collections = list(collections or [])
		self._views = memory.Driver(views or {})

	def items(self) -> list[Item]:
		return self._items

	def collections(self) -> list[Collection]:
		return self._collections

	def views(self) -> memory.Driver:
		return self._views
