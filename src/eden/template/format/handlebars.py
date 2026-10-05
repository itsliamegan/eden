from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, ClassVar

from pybars import Compiler, strlist

from ..runtime import Runtime
from .format import Compiled, Format


class Format(Format):
	pybars: ClassVar[Compiler] = Compiler()

	def compile(self, source: str) -> Compiled:
		return Compiled(self.pybars.compile(source))


@dataclass
class Compiled(Compiled):
	function: Callable[..., str]

	def execute(self, runtime: Runtime):
		locals = runtime.locals | {"content": safe(runtime.content)}

		runtime.content = self.function(
			locals,
			helpers={
				"content-for": handlebarsify(runtime.content_for),
			},
		)


def handlebarsify(helper: Callable[..., object]) -> Callable[..., strlist]:
	def wrapped_helper(context: Any, *args: Any, **kwargs: Any) -> strlist:
		arguments = list(args)

		if was_called_as_block_helper(arguments):
			options = arguments.pop(0)
			content = options["fn"](context)
			arguments.append(content)

		value = helper(*arguments, **kwargs)
		return safe(value)

	return wrapped_helper


def was_called_as_block_helper(args: list[Any]) -> bool:
	return len(args) > 0 and isinstance(args[0], dict) and "fn" in args[0]


def safe(value: object) -> strlist:
	return strlist([str(value)])
