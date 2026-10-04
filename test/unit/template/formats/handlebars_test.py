from websites.template import Registry, compile, formats


def test_renders_evaluated_handlebars():
	registry = Registry()
	template = compile("<h1>{{title}}</h1>\n", formats.handlebars)
	rendered = template.render(registry, {"title": "Home"})

	assert rendered == "<h1>Home</h1>\n"
