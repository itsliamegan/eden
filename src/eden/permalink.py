from enum import Enum, auto


class Permalink:
	@staticmethod
	def root() -> Permalink:
		return Permalink(Kind.INDEX, [])

	def __init__(self, kind: Kind, components: list[str]):
		self.kind = kind
		self.components = components
		self.is_index = kind == Kind.INDEX

	def join(self, component: str) -> Permalink:
		return Permalink(Kind.ENTRY, self.components + [component])

	def to_index(self) -> Permalink:
		return Permalink(Kind.INDEX, self.components.copy())

	def __eq__(self, other: object) -> bool:
		if not isinstance(other, Permalink):
			return NotImplemented

		return self.kind == other.kind and self.components == other.components

	def __str__(self) -> str:
		if len(self.components) == 0:
			return "/"

		inner_path = "/".join(self.components)
		path = "/" + inner_path

		if self.kind == Kind.INDEX:
			path += "/"

		return path


class Kind(Enum):
	INDEX = auto()
	ENTRY = auto()
