from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from .item import Item
from .items import Items


@dataclass
class Collection:
	"""A directory in a site's content. Includes its items and its index.

	Operations return Items, rather than Collection, because a sorted or joined
	sequence is no longer a directory and has no name or index item.
	"""

	name: str
	items: Items
	index: Item | None = None

	def sort(self, field: str) -> Items:
		return self.items.sort(field)

	def reverse(self) -> Items:
		return self.items.reverse()

	def concat(self, other: Iterable[Item]) -> Items:
		return self.items.concat(other)

	def __iter__(self) -> Iterator[Item]:
		return iter(self.items)
