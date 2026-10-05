from luna.test.assertion import assert_eq

from eden.template import Registry, Template
from eden.template.format import markdown


def test_renders_parsed_markdown():
	registry = Registry()
	template = Template.compile("Hello, world!", markdown.Format())
	rendered = template.render(registry)

	assert_eq(rendered, "<p>Hello, world!</p>\n")
