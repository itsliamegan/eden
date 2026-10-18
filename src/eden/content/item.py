from dataclasses import dataclass
import re
import tomllib
from typing import Any, Self, TYPE_CHECKING

from markupsafe import Markup

from .error import ContentError
from .path import ContentPath

if TYPE_CHECKING:
	from ..markdown import Heading

FRONT_MATTER = re.compile(r"\+\+\+\n(.*?)^\+\+\+$\n?", re.DOTALL | re.MULTILINE)


@dataclass
class Item:
	"""A file in a site's content.

	An Item's name is its path's last segment. An item's body and headings are
	set when its site reads it. Two items are equal if their paths are equal.
	"""

	path: ContentPath
	fields: dict[str, Any]
	text: str
	body: Markup | None = None
	headings: list[Heading] | None = None

	@classmethod
	def markdown(cls, path: ContentPath, text: str) -> Self:
		if text.startswith("+++\n"):
			match = FRONT_MATTER.match(text)
			if match is None:
				raise ContentError(f"front matter not closed: {path}")
			return cls(path, cls.load_fields(path, match[1]), text[match.end() :])
		else:
			return cls(path, {}, text)

	@classmethod
	def toml(cls, path: ContentPath, text: str) -> Self:
		return cls(path, cls.load_fields(path, text), "")

	@staticmethod
	def load_fields(path: ContentPath, text: str) -> dict[str, Any]:
		try:
			return tomllib.loads(text)
		except tomllib.TOMLDecodeError as error:
			raise ContentError(f"invalid TOML in {path}: {error}") from error

	@property
	def name(self) -> str:
		return self.path.name

	def field(self, name: str) -> Any:
		return self.fields.get(name)

	def __eq__(self, other: object) -> bool:
		if not isinstance(other, Item):
			return NotImplemented
		return self.path == other.path
