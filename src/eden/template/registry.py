from .template import Template


class Registry:
	templates: dict[str, Template]

	def __init__(self):
		self.templates = {}

	def find(self, name: str) -> Template | None:
		if name in self.templates:
			return self.templates[name]
		else:
			return None

	def add(self, name: str, template: Template):
		self.templates[name] = template
