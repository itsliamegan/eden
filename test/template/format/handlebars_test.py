from luna.test.assertion import assert_eq

from eden.template import Registry, Template
from eden.template.format import handlebars


def test_renders_evaluated_handlebars():
	registry = Registry()
	template = Template.compile("<h1>{{title}}</h1>\n", handlebars.Format())
	rendered = template.render(registry, {"title": "Home"})

	assert_eq(rendered, "<h1>Home</h1>\n")
