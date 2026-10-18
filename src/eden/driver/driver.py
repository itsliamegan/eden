from abc import ABC, abstractmethod

from helios import view

from ..content import Collection, Item


class Driver(ABC):
	"""A place a site is read from.

	Items are those at the top of the content. Each collection holds its own
	items and its index item, and a nested collection is a collection of its
	own, so an index item comes only through its collection.
	"""

	@abstractmethod
	def items(self) -> list[Item]: ...

	@abstractmethod
	def collections(self) -> list[Collection]: ...

	@abstractmethod
	def views(self) -> view.Driver: ...
