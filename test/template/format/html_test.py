from luna.test.assertion import assert_eq

from eden.template import Registry, Template
from eden.template.format import html


def test_renders_html_verbatim():
	registry = Registry()
	template = Template.compile("<h1>About</h1>", html.Format())
	rendered = template.render(registry)

	assert_eq(rendered, "<h1>About</h1>")
