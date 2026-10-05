from eden.template import Registry, Template
from eden.template.format import markdown


def test_renders_parsed_markdown():
	registry = Registry()
	template = Template.compile("Hello, world!", markdown.Format())
	rendered = template.render(registry)

	assert rendered == "<p>Hello, world!</p>\n"
