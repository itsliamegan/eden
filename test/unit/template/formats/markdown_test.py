from eden.template import Registry, compile, formats


def test_renders_parsed_markdown():
	registry = Registry()
	template = compile("Hello, world!", formats.markdown)
	rendered = template.render(registry)

	assert rendered == "<p>Hello, world!</p>\n"
