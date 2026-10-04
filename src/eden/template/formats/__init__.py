from . import handlebars, html, markdown


def by_suffix(file):
	if file.suffix == ".html":
		return html
	elif file.suffix == ".md":
		return markdown
	elif file.suffix == ".hbs":
		return handlebars
