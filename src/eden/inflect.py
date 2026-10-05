def titleize(name: str) -> str:
	words = name.split("_")
	capitalized_words = (word.capitalize() for word in words)
	title = " ".join(capitalized_words)

	return title


def dasherize(name: str) -> str:
	lowercased = name.lower()
	dashed = lowercased.replace("_", "-")

	return dashed
