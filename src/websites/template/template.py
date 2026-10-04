from .runtime import Runtime

def compile(source, format, parent=None):
	compiled = format.compile(source)
	return Template(compiled, format, parent)

class Template:
	def __init__(self, compiled, format, parent):
		self.compiled = compiled
		self.format = format
		self.parent = parent

	def render(self, registry, locals=None):
		if locals is None:
			locals = {}

		runtime = Runtime(locals)
		template = self

		while template is not None:
			template.execute(runtime)
			template = registry.find(template.parent)

		return runtime.content
		

	def execute(self, runtime):
		self.format.execute(self.compiled, runtime)
