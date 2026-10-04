from eden.template import Registry, compile, formats


def test_passes_rendered_content_to_parent():
	registry = Registry()
	child = compile("Hello, world!", formats.markdown, parent="article")
	parent = compile("<article>{{content}}</article>", formats.handlebars)
	registry.add("article", parent)
	rendered = child.render(registry)

	assert rendered == "<article><p>Hello, world!</p>\n</article>"


def test_passes_sections_to_parent():
	registry = Registry()
	child = compile(
		'{{#content-for "header"}}<h1>About</h1>{{/content-for}}',
		formats.handlebars,
		parent="main",
	)
	parent = compile('<header>{{content-for "header"}}</header>', formats.handlebars)
	registry.add("main", parent)
	rendered = child.render(registry)

	assert rendered == "<header><h1>About</h1></header>"
