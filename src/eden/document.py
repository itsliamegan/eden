from .permalink import Permalink


class Document:
	def __init__(self, permalink: Permalink, contents: str):
		self.permalink = permalink
		self.contents = contents
