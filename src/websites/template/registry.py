class Registry:
	def __init__(self):
		self.templates = {}

	def find(self, name):
		if name in self.templates:
			return self.templates[name]
		else:
			return None

	def add(self, name, template):
		self.templates[name] = template
