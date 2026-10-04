from abc import ABC, abstractmethod
from pathlib import Path

from ..runtime import Runtime


class Format(ABC):
	@staticmethod
	def for_file(file: Path) -> Format:
		from . import handlebars, html, markdown

		match file.suffix:
			case ".html":
				return html.Format()
			case ".md":
				return markdown.Format()
			case ".hbs":
				return handlebars.Format()
			case _:
				raise ValueError(f"Unknown template format: {file.suffix}")

	@abstractmethod
	def compile(self, source: str) -> Compiled: ...


class Compiled(ABC):
	@abstractmethod
	def execute(self, runtime: Runtime): ...
