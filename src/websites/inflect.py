def titleize(name):
	words = name.split("_")
	capitalized_words = (word.capitalize() for word in words)
	title = " ".join(capitalized_words)

	return title

def dasherize(name):
	lowercased = name.lower()
	dashed = lowercased.replace("_", "-")

	return dashed
