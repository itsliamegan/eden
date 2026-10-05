from dataclasses import dataclass
from typing import Self


@dataclass
class Permalink:
	segments: list[str]
	is_index: bool = False

	@classmethod
	def root(cls) -> Self:
		return cls([], is_index=True)

	def join(self, segment: str) -> Permalink:
		return Permalink(self.segments + [segment])

	def to_index(self) -> Permalink:
		return Permalink(self.segments.copy(), is_index=True)

	def __str__(self) -> str:
		if len(self.segments) == 0:
			return "/"

		inner_path = "/".join(self.segments)
		path = "/" + inner_path

		if self.is_index:
			path += "/"

		return path
