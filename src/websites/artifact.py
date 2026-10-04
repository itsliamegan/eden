class Site:
	def __init__(self):
		self.documents = []

	def add_document(self, document):
		self.documents.append(document)

class Document:
	def __init__(self, permalink, contents):
		self.permalink = permalink
		self.contents = contents
