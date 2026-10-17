from helios.view import Engine, file, memory
from luna.test.assertion import assert_eq, assert_is

from eden.content import ContentPath, Item
from eden.markdown import Renderer, VIEWS_DIR


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


def test_renders_fenced_code():
	renderer = Renderer(Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]))
	item = Item.markdown(
		ContentPath.parse("guides/database"),
		"```python\nimport tomllib\n```\n",
	)

	body = renderer.render(item)

	assert_eq(
		body.html,
		'<pre><code class="language-python">import tomllib\n</code></pre>\n',
	)


def test_renders_fenced_code_without_language():
	renderer = Renderer(Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]))
	item = Item.markdown(ContentPath.parse("guides/database"), "```\neden build\n```\n")

	body = renderer.render(item)

	assert_eq(body.html, "<pre><code>eden build\n</code></pre>\n")


def test_renders_indented_code_without_language():
	renderer = Renderer(Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]))
	item = Item.markdown(ContentPath.parse("guides/database"), "    eden build\n")

	body = renderer.render(item)

	assert_eq(body.html, "<pre><code>eden build\n</code></pre>\n")


def test_keeps_entities_in_code_as_written():
	renderer = Renderer(Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]))
	item = Item.markdown(ContentPath.parse("guides/database"), "```\n&amp;\n```\n")

	body = renderer.render(item)

	assert_eq(body.html, "<pre><code>&amp;amp;\n</code></pre>\n")


def test_renders_heading():
	renderer = Renderer(Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]))
	item = Item.markdown(ContentPath.parse("guides/database"), "## Getting started\n")

	body = renderer.render(item)

	assert_eq(body.html, '<h2 id="getting-started">Getting started</h2>\n')


def test_collects_headings():
	renderer = Renderer(Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]))
	item = Item.markdown(
		ContentPath.parse("guides/database"),
		"# Database\n\n## Getting *started*\n",
	)

	body = renderer.render(item)

	assert_eq(len(body.headings), 2)
	assert_eq(body.headings[0].level, 1)
	assert_eq(body.headings[0].id, "database")
	assert_eq(body.headings[0].text, "Database")
	assert_eq(body.headings[1].level, 2)
	assert_eq(body.headings[1].id, "getting-started")
	assert_eq(body.headings[1].text, "Getting started")
	assert_eq(body.headings[1].content, "Getting <em>started</em>")


def test_numbers_repeated_heading_ids():
	renderer = Renderer(Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]))
	item = Item.markdown(
		ContentPath.parse("guides/database"),
		"## Setup\n\n## Setup\n",
	)

	body = renderer.render(item)

	assert_eq(body.headings[0].id, "setup")
	assert_eq(body.headings[1].id, "setup-1")


def test_numbers_repeated_heading_id_past_written_one():
	renderer = Renderer(Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]))
	item = Item.markdown(
		ContentPath.parse("guides/database"),
		"## Setup\n\n## Setup 1\n\n## Setup\n",
	)

	body = renderer.render(item)

	assert_eq(body.headings[2].id, "setup-2")


def test_numbers_heading_ids_per_item():
	renderer = Renderer(Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]))
	renderer.render(Item.markdown(ContentPath.parse("guides/database"), "## Setup\n"))
	item = Item.markdown(ContentPath.parse("guides/routing"), "## Setup\n")

	body = renderer.render(item)

	assert_eq(body.headings[0].id, "setup")


def test_gives_heading_without_letters_no_id():
	renderer = Renderer(Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]))
	item = Item.markdown(ContentPath.parse("guides/database"), "## ...\n")

	body = renderer.render(item)

	assert_is(body.headings[0].id, None)


def test_leaves_headings_without_ids_unnumbered():
	renderer = Renderer(Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]))
	item = Item.markdown(ContentPath.parse("guides/database"), "## ...\n\n## ...\n")

	body = renderer.render(item)

	assert_is(body.headings[1].id, None)


def test_renders_image():
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


def test_renders_image_without_title():
	renderer = Renderer(Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]))
	item = Item.markdown(
		ContentPath.parse("writing/tranquility"),
		"![A lake](lake.jpg)\n",
	)

	body = renderer.render(item)

	assert_eq(body.html, '<p><img src="lake.jpg" alt="A lake"></p>\n')


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
