from dataclasses import dataclass
from typing import Self, TYPE_CHECKING

from .format import Compiled, Format
from .runtime import Runtime

if TYPE_CHECKING:
	from .registry import Registry


@dataclass
class Template:
	compiled: Compiled
	parent: str | None = None

	@classmethod
	def compile(cls, source: str, format: Format, parent: str | None = None) -> Self:
		return cls(format.compile(source), parent=parent)

	def render(
		self,
		registry: Registry,
		locals: dict[str, object] | None = None,
	) -> str:
		locals = locals or {}
		runtime = Runtime(locals)

		template: Template | None = self
		while template is not None:
			template.compiled.execute(runtime)

			if template.parent is None:
				template = None
			else:
				template = registry.find(template.parent)

		return runtime.content
