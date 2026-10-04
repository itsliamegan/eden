from .permalink import Permalink


class Site:
	documents: list[Document]

	def __init__(self):
		self.documents = []

	def add_document(self, document: Document):
		self.documents.append(document)


class Document:
	def __init__(self, permalink: Permalink, contents: str):
		self.permalink = permalink
		self.contents = contents
