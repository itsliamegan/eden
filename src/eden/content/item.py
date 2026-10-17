from dataclasses import dataclass
import re
import tomllib
from typing import Any, Self

from .error import ContentError


@dataclass
class Item:
	"""One file in a site's content, named by its path without the extension.

	Two items are equal when their paths are.
	"""

	path: str
	fields: dict[str, Any]
	text: str

	@classmethod
	def markdown(cls, path: str, text: str) -> Self:
		if not text.startswith("+++\n"):
			return cls(path, {}, text)

		match = FRONT_MATTER.match(text)
		if match is None:
			raise ContentError(f"front matter not closed: {path}")
		return cls(path, tomllib.loads(match[1]), text[match.end() :])

	@classmethod
	def toml(cls, path: str, text: str) -> Self:
		return cls(path, tomllib.loads(text), "")

	@property
	def name(self) -> str:
		return self.path.rpartition("/")[2]

	def field(self, name: str) -> Any:
		return self.fields.get(name)

	def __eq__(self, other: object) -> bool:
		if not isinstance(other, Item):
			return NotImplemented
		return self.path == other.path


FRONT_MATTER = re.compile(r"\+\+\+\n(.*?)^\+\+\+$\n?", re.DOTALL | re.MULTILINE)
