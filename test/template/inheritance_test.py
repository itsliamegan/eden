from luna.test.assertion import assert_eq

from eden.template import Registry, Template
from eden.template.format import handlebars, markdown


def test_passes_rendered_content_to_parent():
	registry = Registry()
	child = Template.compile("Hello, world!", markdown.Format(), parent="article")
	parent = Template.compile("<article>{{content}}</article>", handlebars.Format())
	registry.add("article", parent)
	rendered = child.render(registry)

	assert_eq(rendered, "<article><p>Hello, world!</p>\n</article>")


def test_passes_sections_to_parent():
	registry = Registry()
	child = Template.compile(
		'{{#content-for "header"}}<h1>About</h1>{{/content-for}}',
		handlebars.Format(),
		parent="main",
	)
	parent = Template.compile(
		'<header>{{content-for "header"}}</header>',
		handlebars.Format(),
	)
	registry.add("main", parent)
	rendered = child.render(registry)

	assert_eq(rendered, "<header><h1>About</h1></header>")
