class Runtime:
	def __init__(self, locals):
		self.locals = locals
		self.content = ""
		self.sections = {}

	def content_for(self, section, content=None):
		if content is None:
			return self.sections[section]
		else:
			self.sections[section] = content
