from helios.view import Engine, memory
from luna.test.assertion import assert_eq

from eden.content import ContentPath, Item
from eden.markdown import Renderer


def test_renders_plain_elements():
	renderer = Renderer(Engine(memory.Driver({})))
	item = Item.markdown(ContentPath.parse("writing/tranquility"), "Still *water*.\n")

	body = renderer.render(item)

	assert_eq(body.html, "<p>Still <em>water</em>.</p>\n")


def test_passes_raw_html_through():
	renderer = Renderer(Engine(memory.Driver({})))
	item = Item.markdown(
		ContentPath.parse("writing/tranquility"),
		'<aside class="note">\n<script>quiet()</script>\n</aside>\n',
	)

	body = renderer.render(item)

	assert_eq(
		body.html,
		'<aside class="note">\n<script>quiet()</script>\n</aside>\n',
	)


def test_renders_fenced_code_through_component():
	renderer = Renderer(
		Engine(
			memory.Driver(
				{"components/markdown/code": "[{{ language }}] {{ code }}"},
			)
		)
	)
	item = Item.markdown(
		ContentPath.parse("guides/database"),
		"```python\nprint(1 < 2)\n```\n",
	)

	body = renderer.render(item)

	assert_eq(body.html, "[python] print(1 &lt; 2)\n\n")


def test_renders_fenced_code_without_language():
	renderer = Renderer(
		Engine(
			memory.Driver(
				{"components/markdown/code": "[{{ language }}] {{ code }}"},
			)
		)
	)
	item = Item.markdown(ContentPath.parse("guides/database"), "```\neden build\n```\n")

	body = renderer.render(item)

	assert_eq(body.html, "[] eden build\n\n")


def test_renders_indented_code_without_language():
	renderer = Renderer(
		Engine(
			memory.Driver(
				{"components/markdown/code": "[{{ language }}] {{ code }}"},
			)
		)
	)
	item = Item.markdown(ContentPath.parse("guides/database"), "    eden build\n")

	body = renderer.render(item)

	assert_eq(body.html, "[] eden build\n\n")


def test_keeps_entities_in_code_as_written():
	renderer = Renderer(
		Engine(
			memory.Driver(
				{"components/markdown/code": "[{{ language }}] {{ code }}"},
			)
		)
	)
	item = Item.markdown(ContentPath.parse("guides/database"), "```\n&amp;\n```\n")

	body = renderer.render(item)

	assert_eq(body.html, "[] &amp;amp;\n\n")


def test_renders_image_through_component():
	renderer = Renderer(
		Engine(
			memory.Driver(
				{"components/markdown/image": "[{{ src }}] [{{ alt }}] [{{ title }}]"},
			)
		)
	)
	item = Item.markdown(
		ContentPath.parse("writing/tranquility"),
		'![A lake](lake.jpg "At dawn")\n',
	)

	body = renderer.render(item)

	assert_eq(body.html, "<p>[lake.jpg] [A lake] [At dawn]</p>\n")


def test_renders_image_without_title():
	renderer = Renderer(
		Engine(
			memory.Driver(
				{"components/markdown/image": "[{{ src }}] [{{ alt }}] [{{ title }}]"},
			)
		)
	)
	item = Item.markdown(
		ContentPath.parse("writing/tranquility"),
		"![A lake](lake.jpg)\n",
	)

	body = renderer.render(item)

	assert_eq(body.html, "<p>[lake.jpg] [A lake] []</p>\n")


def test_renders_image_alt_as_plain_text():
	renderer = Renderer(
		Engine(
			memory.Driver(
				{"components/markdown/image": "[{{ src }}] [{{ alt }}] [{{ title }}]"},
			)
		)
	)
	item = Item.markdown(
		ContentPath.parse("writing/tranquility"),
		"![A *still* lake &amp; `dock`](lake.jpg)\n",
	)

	body = renderer.render(item)

	assert_eq(body.html, "<p>[lake.jpg] [A still lake &amp; dock] []</p>\n")
