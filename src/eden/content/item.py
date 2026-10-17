from dataclasses import dataclass
import re
import tomllib
from typing import Any, Self

from .error import ContentError
from .path import ContentPath

FRONT_MATTER = re.compile(r"\+\+\+\n(.*?)^\+\+\+$\n?", re.DOTALL | re.MULTILINE)


@dataclass
class Item:
	"""A file in a site's content.

	An Item's name is its path's last segment. Two items are equal if their
	paths are equal.
	"""

	path: ContentPath
	fields: dict[str, Any]
	text: str

	@classmethod
	def markdown(cls, path: ContentPath, text: str) -> Self:
		if text.startswith("+++\n"):
			match = FRONT_MATTER.match(text)
			if match is None:
				raise ContentError(f"front matter not closed: {path}")
			return cls(path, tomllib.loads(match[1]), text[match.end() :])
		else:
			return cls(path, {}, text)

	@classmethod
	def toml(cls, path: ContentPath, text: str) -> Self:
		return cls(path, tomllib.loads(text), "")

	@property
	def name(self) -> str:
		return self.path.name

	def field(self, name: str) -> Any:
		return self.fields.get(name)

	def __eq__(self, other: object) -> bool:
		if not isinstance(other, Item):
			return NotImplemented
		return self.path == other.path
