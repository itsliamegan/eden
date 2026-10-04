class Runtime:
	sections: dict[str, str]

	def __init__(self, locals: dict[str, object]):
		self.locals = locals
		self.content = ""
		self.sections = {}

	def content_for(self, section: str, content: str | None = None) -> str | None:
		if content is None:
			return self.sections[section]
		else:
			self.sections[section] = content
