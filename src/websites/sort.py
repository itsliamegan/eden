class Sort:
	@staticmethod
	def default():
		return Default()

	@staticmethod
	def ascending_by(attr):
		return AscendingBy(attr)

	@staticmethod
	def descending_by(attr):
		return DescendingBy(attr)

class Default:
	def __call__(self, iter):
		return iter

class AscendingBy:
	def __init__(self, attr):
		self.attr = attr

	def __call__(self, iter):
		return sorted(iter, key=lambda item: getattr(item, self.attr))

class DescendingBy:
	def __init__(self, attr):
		self.attr = attr

	def __call__(self, iter):
		return sorted(iter, key=lambda item: getattr(item, self.attr), reverse=True)
