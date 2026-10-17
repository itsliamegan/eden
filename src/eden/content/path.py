from dataclasses import dataclass
from typing import Self

from .error import ContentError


@dataclass
class ContentPath:
	"""A place in a site's content, which names an item or a collection.

	It is a file's or a directory's path in the content, without the extension.
	"""

	segments: tuple[str, ...]

	@classmethod
	def parse(cls, text: str) -> Self:
		segments = tuple(text.split("/"))
		for segment in segments:
			if segment in ("", ".", ".."):
				raise ContentError(f"invalid content path: {text}")

		return cls(segments)

	@property
	def name(self) -> str:
		return self.segments[-1]

	@property
	def parent(self) -> ContentPath | None:
		if len(self.segments) == 1:
			return None
		else:
			return ContentPath(self.segments[:-1])

	def __str__(self) -> str:
		return "/".join(self.segments)

	def __hash__(self) -> int:
		return hash(self.segments)
