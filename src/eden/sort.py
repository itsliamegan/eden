from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass


class Sort(ABC):
	@abstractmethod
	def apply[T](self, items: Iterable[T]) -> Iterable[T]: ...


class Default(Sort):
	def apply[T](self, items: Iterable[T]) -> Iterable[T]:
		return items


@dataclass
class AscendingBy(Sort):
	attribute: str

	def apply[T](self, items: Iterable[T]) -> Iterable[T]:
		return sorted(items, key=lambda item: getattr(item, self.attribute))


@dataclass
class DescendingBy(Sort):
	attribute: str

	def apply[T](self, items: Iterable[T]) -> Iterable[T]:
		return sorted(
			items,
			key=lambda item: getattr(item, self.attribute),
			reverse=True,
		)
