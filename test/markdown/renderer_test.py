from helios.view import Engine, file, memory
from luna.test.assertion import assert_eq

from eden.content import ContentPath, Item
from eden.markdown import Renderer, VIEWS_DIR


def test_renders_plain_elements():
	renderer = Renderer(Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]))
	item = Item.markdown(ContentPath.parse("writing/tranquility"), "Still *water*.\n")

	body = renderer.render(item)

	assert_eq(body.html, "<p>Still <em>water</em>.</p>\n")


def test_passes_raw_html_through():
	renderer = Renderer(Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]))
	item = Item.markdown(
		ContentPath.parse("writing/tranquility"),
		'<aside class="note">\n<script>quiet()</script>\n</aside>\n',
	)

	body = renderer.render(item)

	assert_eq(
		body.html,
		'<aside class="note">\n<script>quiet()</script>\n</aside>\n',
	)


def test_renders_fenced_code():
	renderer = Renderer(Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]))
	item = Item.markdown(
		ContentPath.parse("guides/database"),
		"```python\nprint(1 < 2)\n```\n",
	)

	body = renderer.render(item)

	assert_eq(
		body.html,
		'<pre><code class="language-python">print(1 &lt; 2)\n</code></pre>\n',
	)


def test_renders_fenced_code_without_language():
	renderer = Renderer(Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]))
	item = Item.markdown(ContentPath.parse("guides/database"), "```\neden build\n```\n")

	body = renderer.render(item)

	assert_eq(body.html, "<pre><code>eden build\n</code></pre>\n")


def test_keeps_entities_in_code_as_written():
	renderer = Renderer(Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]))
	item = Item.markdown(ContentPath.parse("guides/database"), "```\n&amp;\n```\n")

	body = renderer.render(item)

	assert_eq(body.html, "<pre><code>&amp;amp;\n</code></pre>\n")


def test_renders_indented_code_without_language():
	renderer = Renderer(Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]))
	item = Item.markdown(ContentPath.parse("guides/database"), "    eden build\n")

	body = renderer.render(item)

	assert_eq(body.html, "<pre><code>eden build\n</code></pre>\n")


def test_renders_image():
	renderer = Renderer(Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]))
	item = Item.markdown(
		ContentPath.parse("writing/tranquility"),
		"![A lake](lake.jpg)\n",
	)

	body = renderer.render(item)

	assert_eq(body.html, '<p><img src="lake.jpg" alt="A lake"></p>\n')


def test_renders_image_with_title():
	renderer = Renderer(Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]))
	item = Item.markdown(
		ContentPath.parse("writing/tranquility"),
		'![A lake](lake.jpg "At dawn")\n',
	)

	body = renderer.render(item)

	assert_eq(
		body.html,
		'<p><img src="lake.jpg" alt="A lake" title="At dawn"></p>\n',
	)


def test_renders_image_alt_as_plain_text():
	renderer = Renderer(Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]))
	item = Item.markdown(
		ContentPath.parse("writing/tranquility"),
		"![A *still* lake &amp; `dock`](lake.jpg)\n",
	)

	body = renderer.render(item)

	assert_eq(
		body.html,
		'<p><img src="lake.jpg" alt="A still lake &amp; dock"></p>\n',
	)


def test_renders_through_site_template():
	renderer = Renderer(
		Engine(
			memory.Driver({"components/markdown/image": "<figure>{{ alt }}</figure>"}),
			fallbacks=[file.Driver(VIEWS_DIR)],
		)
	)
	item = Item.markdown(
		ContentPath.parse("writing/tranquility"),
		"![A lake](lake.jpg)\n",
	)

	body = renderer.render(item)

	assert_eq(body.html, "<p><figure>A lake</figure></p>\n")
