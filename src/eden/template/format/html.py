from dataclasses import dataclass

from ..runtime import Runtime
from .format import Compiled, Format


class Format(Format):
	def compile(self, source: str) -> Compiled:
		return Compiled(source)


@dataclass
class Compiled(Compiled):
	html: str

	def execute(self, runtime: Runtime):
		runtime.content = self.html
