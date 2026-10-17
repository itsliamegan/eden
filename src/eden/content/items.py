from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from .error import ContentError
from .item import Item


@dataclass
class Items:
	"""A sequence of items in order, whose operations each return a new one."""

	items: list[Item]

	def sort(self, field: str) -> Items:
		for item in self.items:
			if item.field(field) is None:
				raise ContentError(f"field not set: {field} in {item.path}")

		try:
			items = sorted(self.items, key=lambda item: item.field(field))
		except TypeError as error:
			raise ContentError(f"field values not comparable: {field}") from error
		return Items(items)

	def reverse(self) -> Items:
		return Items(list(reversed(self.items)))

	def concat(self, other: Iterable[Item]) -> Items:
		return Items([*self.items, *other])

	def __iter__(self) -> Iterator[Item]:
		return iter(self.items)
