from dataclasses import dataclass
from pathlib import Path

from .permalink import Permalink


@dataclass
class Document:
	permalink: Permalink
	contents: str

	@property
	def path(self) -> Path:
		if self.permalink.is_index:
			return Path(*self.permalink.segments, "index.html")
		else:
			*directories, name = self.permalink.segments
			return Path(*directories, name + ".html")
