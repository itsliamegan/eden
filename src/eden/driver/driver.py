from abc import ABC, abstractmethod

from helios import view

from ..content import Collection, Item


class Driver(ABC):
	"""An interface for accessing the resources of a site."""

	@abstractmethod
	def items(self) -> list[Item]: ...

	@abstractmethod
	def collections(self) -> list[Collection]: ...

	@abstractmethod
	def views(self) -> view.Driver: ...
