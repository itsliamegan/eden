from dataclasses import dataclass

from .permalink import Permalink


@dataclass
class Document:
	permalink: Permalink
	contents: str
