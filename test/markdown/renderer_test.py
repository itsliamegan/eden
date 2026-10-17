from helios.url import Pattern, URL
from helios.view import Engine, file, memory
from luna.test.assertion import assert_eq, assert_is

from eden.content import ContentPath, Item
from eden.markdown import Destinations, Renderer, VIEWS_DIR
from eden.routing import Route, URLs
from eden.routing.route import PerItemExpansion


def test_renders_plain_elements():
	renderer = Renderer(
		Engine(memory.Driver({})),
		Destinations(URLs([], URL.parse("https://example.com")), {}),
	)
	item = Item.markdown(ContentPath.parse("articles/intro"), "Read *this* first.\n")

	body = renderer.render(item)

	assert_eq(body.html, "<p>Read <em>this</em> first.</p>\n")


def test_passes_raw_html_through():
	renderer = Renderer(
		Engine(memory.Driver({})),
		Destinations(URLs([], URL.parse("https://example.com")), {}),
	)
	item = Item.markdown(
		ContentPath.parse("articles/intro"),
		'<aside class="note">\n<script>highlight()</script>\n</aside>\n',
	)

	body = renderer.render(item)

	assert_eq(
		body.html,
		'<aside class="note">\n<script>highlight()</script>\n</aside>\n',
	)


def test_renders_table():
	renderer = Renderer(
		Engine(memory.Driver({})),
		Destinations(URLs([], URL.parse("https://example.com")), {}),
	)
	item = Item.markdown(
		ContentPath.parse("articles/intro"),
		"| Command | Effect |\n| :-- | --: |\n| `eden build` | Writes *public* |\n",
	)

	body = renderer.render(item)

	assert_eq(
		body.html,
		"<table>\n<thead>\n<tr>\n"
		'<th align="left">Command</th>\n<th align="right">Effect</th>\n'
		"</tr>\n</thead>\n<tbody>\n<tr>\n"
		'<td align="left"><code>eden build</code></td>\n'
		'<td align="right">Writes <em>public</em></td>\n'
		"</tr>\n</tbody></table>",
	)


def test_renders_fenced_code():
	renderer = Renderer(
		Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]),
		Destinations(URLs([], URL.parse("https://example.com")), {}),
	)
	item = Item.markdown(
		ContentPath.parse("articles/intro"),
		"```python\nimport tomllib\n```\n",
	)

	body = renderer.render(item)

	assert_eq(
		body.html,
		'<pre><code class="language-python">import tomllib\n</code></pre>\n',
	)


def test_renders_fenced_code_without_language():
	renderer = Renderer(
		Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]),
		Destinations(URLs([], URL.parse("https://example.com")), {}),
	)
	item = Item.markdown(ContentPath.parse("articles/intro"), "```\neden build\n```\n")

	body = renderer.render(item)

	assert_eq(body.html, "<pre><code>eden build\n</code></pre>\n")


def test_renders_indented_code_without_language():
	renderer = Renderer(
		Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]),
		Destinations(URLs([], URL.parse("https://example.com")), {}),
	)
	item = Item.markdown(ContentPath.parse("articles/intro"), "    eden build\n")

	body = renderer.render(item)

	assert_eq(body.html, "<pre><code>eden build\n</code></pre>\n")


def test_keeps_entities_in_code_as_written():
	renderer = Renderer(
		Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]),
		Destinations(URLs([], URL.parse("https://example.com")), {}),
	)
	item = Item.markdown(ContentPath.parse("articles/intro"), "```\n&amp;\n```\n")

	body = renderer.render(item)

	assert_eq(body.html, "<pre><code>&amp;amp;\n</code></pre>\n")


def test_renders_heading():
	renderer = Renderer(
		Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]),
		Destinations(URLs([], URL.parse("https://example.com")), {}),
	)
	item = Item.markdown(ContentPath.parse("articles/intro"), "## Getting started\n")

	body = renderer.render(item)

	assert_eq(body.html, '<h2 id="getting-started">Getting started</h2>\n')


def test_collects_headings():
	renderer = Renderer(
		Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]),
		Destinations(URLs([], URL.parse("https://example.com")), {}),
	)
	item = Item.markdown(
		ContentPath.parse("articles/intro"),
		"# Intro\n\n## Getting *started*\n",
	)

	body = renderer.render(item)

	assert_eq(len(body.headings), 2)
	assert_eq(body.headings[0].level, 1)
	assert_eq(body.headings[0].id, "intro")
	assert_eq(body.headings[0].text, "Intro")
	assert_eq(body.headings[1].level, 2)
	assert_eq(body.headings[1].id, "getting-started")
	assert_eq(body.headings[1].text, "Getting started")
	assert_eq(body.headings[1].content, "Getting <em>started</em>")


def test_numbers_repeated_heading_ids():
	renderer = Renderer(
		Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]),
		Destinations(URLs([], URL.parse("https://example.com")), {}),
	)
	item = Item.markdown(
		ContentPath.parse("articles/intro"),
		"## Setup\n\n## Setup\n",
	)

	body = renderer.render(item)

	assert_eq(body.headings[0].id, "setup")
	assert_eq(body.headings[1].id, "setup-1")


def test_numbers_repeated_heading_id_past_written_one():
	renderer = Renderer(
		Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]),
		Destinations(URLs([], URL.parse("https://example.com")), {}),
	)
	item = Item.markdown(
		ContentPath.parse("articles/intro"),
		"## Setup\n\n## Setup 1\n\n## Setup\n",
	)

	body = renderer.render(item)

	assert_eq(body.headings[2].id, "setup-2")


def test_numbers_heading_ids_per_item():
	renderer = Renderer(
		Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]),
		Destinations(URLs([], URL.parse("https://example.com")), {}),
	)
	renderer.render(Item.markdown(ContentPath.parse("articles/intro"), "## Setup\n"))
	item = Item.markdown(ContentPath.parse("articles/outro"), "## Setup\n")

	body = renderer.render(item)

	assert_eq(body.headings[0].id, "setup")


def test_gives_heading_without_letters_no_id():
	renderer = Renderer(
		Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]),
		Destinations(URLs([], URL.parse("https://example.com")), {}),
	)
	item = Item.markdown(ContentPath.parse("articles/intro"), "## ...\n")

	body = renderer.render(item)

	assert_is(body.headings[0].id, None)


def test_leaves_headings_without_ids_unnumbered():
	renderer = Renderer(
		Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]),
		Destinations(URLs([], URL.parse("https://example.com")), {}),
	)
	item = Item.markdown(ContentPath.parse("articles/intro"), "## ...\n\n## ...\n")

	body = renderer.render(item)

	assert_is(body.headings[1].id, None)


def test_renders_footnotes():
	renderer = Renderer(
		Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]),
		Destinations(URLs([], URL.parse("https://example.com")), {}),
	)
	item = Item.markdown(
		ContentPath.parse("articles/intro"),
		"Read first.[^source]\n\n[^source]: From the manual.\n",
	)

	body = renderer.render(item)

	assert_eq(
		body.html,
		'<p>Read first.<sup id="fnref-source"><a href="#fn-source">1</a></sup></p>\n'
		'<section class="footnotes">\n<ol>\n'
		'<li id="fn-source">\n<p>From the manual.</p>\n\n<a href="#fnref-source">↩</a>\n</li>\n'
		"</ol>\n</section>\n",
	)


def test_numbers_footnotes_by_first_reference():
	renderer = Renderer(
		Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]),
		Destinations(URLs([], URL.parse("https://example.com")), {}),
	)
	item = Item.markdown(
		ContentPath.parse("articles/intro"),
		"First[^aside] and second[^source].\n\n"
		"[^source]: From the manual.\n\n"
		"[^aside]: An aside.\n",
	)

	body = renderer.render(item)

	assert_eq(
		body.html,
		'<p>First<sup id="fnref-aside"><a href="#fn-aside">1</a></sup> and '
		'second<sup id="fnref-source"><a href="#fn-source">2</a></sup>.</p>\n'
		'<section class="footnotes">\n<ol>\n'
		'<li id="fn-aside">\n<p>An aside.</p>\n\n<a href="#fnref-aside">↩</a>\n</li>\n'
		'<li id="fn-source">\n<p>From the manual.</p>\n\n<a href="#fnref-source">↩</a>\n</li>\n'
		"</ol>\n</section>\n",
	)


def test_keeps_number_of_repeated_footnote_reference():
	renderer = Renderer(
		Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]),
		Destinations(URLs([], URL.parse("https://example.com")), {}),
	)
	item = Item.markdown(
		ContentPath.parse("articles/intro"),
		"Read[^source], then reread[^source].\n\n[^source]: From the manual.\n",
	)

	body = renderer.render(item)

	assert_eq(
		body.html,
		'<p>Read<sup id="fnref-source"><a href="#fn-source">1</a></sup>, '
		'then reread<sup id="fnref-source"><a href="#fn-source">1</a></sup>.</p>\n'
		'<section class="footnotes">\n<ol>\n'
		'<li id="fn-source">\n<p>From the manual.</p>\n\n<a href="#fnref-source">↩</a>\n</li>\n'
		"</ol>\n</section>\n",
	)


def test_drops_unreferenced_footnote():
	renderer = Renderer(
		Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]),
		Destinations(URLs([], URL.parse("https://example.com")), {}),
	)
	item = Item.markdown(
		ContentPath.parse("articles/intro"),
		"Read first.\n\n[^source]: From the manual.\n",
	)

	body = renderer.render(item)

	assert_eq(body.html, "<p>Read first.</p>\n")


def test_lists_footnote_referenced_from_footnote():
	renderer = Renderer(
		Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]),
		Destinations(URLs([], URL.parse("https://example.com")), {}),
	)
	item = Item.markdown(
		ContentPath.parse("articles/intro"),
		"Read[^source].\n\n"
		"[^source]: From the manual.[^aside]\n\n"
		"[^aside]: An aside.\n",
	)

	body = renderer.render(item)

	assert_eq(
		body.html,
		'<p>Read<sup id="fnref-source"><a href="#fn-source">1</a></sup>.</p>\n'
		'<section class="footnotes">\n<ol>\n'
		'<li id="fn-source">\n<p>From the manual.'
		'<sup id="fnref-aside"><a href="#fn-aside">2</a></sup></p>\n\n'
		'<a href="#fnref-source">↩</a>\n</li>\n'
		'<li id="fn-aside">\n<p>An aside.</p>\n\n<a href="#fnref-aside">↩</a>\n</li>\n'
		"</ol>\n</section>\n",
	)


def test_renders_link():
	renderer = Renderer(
		Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]),
		Destinations(URLs([], URL.parse("https://example.com")), {}),
	)
	item = Item.markdown(
		ContentPath.parse("articles/intro"),
		'Read [the *manual*](https://example.org/manual "Start here").\n',
	)

	body = renderer.render(item)

	assert_eq(
		body.html,
		'<p>Read <a href="https://example.org/manual" title="Start here">'
		"the <em>manual</em></a>.</p>\n",
	)


def test_renders_link_without_title():
	renderer = Renderer(
		Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]),
		Destinations(URLs([], URL.parse("https://example.com")), {}),
	)
	item = Item.markdown(
		ContentPath.parse("articles/intro"),
		"[Manual](https://example.org/manual)\n",
	)

	body = renderer.render(item)

	assert_eq(body.html, '<p><a href="https://example.org/manual">Manual</a></p>\n')


def test_renders_autolink():
	renderer = Renderer(
		Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]),
		Destinations(URLs([], URL.parse("https://example.com")), {}),
	)
	item = Item.markdown(
		ContentPath.parse("articles/intro"),
		"<https://example.org/manual>\n",
	)

	body = renderer.render(item)

	assert_eq(
		body.html,
		'<p><a href="https://example.org/manual">https://example.org/manual</a></p>\n',
	)


def test_renders_link_to_item_through_destinations():
	route = Route(
		"article",
		Pattern.parse("/articles/{name}"),
		"articles/show",
		PerItemExpansion(ContentPath.parse("articles")),
	)
	outro = Item(ContentPath.parse("articles/outro"), {}, "")
	renderer = Renderer(
		Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]),
		Destinations(
			URLs([route], URL.parse("https://example.com")),
			{outro.path: outro},
		),
	)
	item = Item.markdown(ContentPath.parse("articles/intro"), "[Outro](outro.md)\n")

	body = renderer.render(item)

	assert_eq(body.html, '<p><a href="/articles/outro">Outro</a></p>\n')


def test_renders_image_path_through_destinations():
	renderer = Renderer(
		Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]),
		Destinations(URLs([], URL.parse("https://example.com/mesa")), {}),
	)
	item = Item.markdown(
		ContentPath.parse("articles/intro"),
		"![A diagram](/diagram.png)\n",
	)

	body = renderer.render(item)

	assert_eq(body.html, '<p><img src="/mesa/diagram.png" alt="A diagram"></p>\n')


def test_renders_image():
	renderer = Renderer(
		Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]),
		Destinations(URLs([], URL.parse("https://example.com")), {}),
	)
	item = Item.markdown(
		ContentPath.parse("articles/intro"),
		'![A diagram](diagram.png "Overview")\n',
	)

	body = renderer.render(item)

	assert_eq(
		body.html,
		'<p><img src="diagram.png" alt="A diagram" title="Overview"></p>\n',
	)


def test_renders_image_without_title():
	renderer = Renderer(
		Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]),
		Destinations(URLs([], URL.parse("https://example.com")), {}),
	)
	item = Item.markdown(
		ContentPath.parse("articles/intro"),
		"![A diagram](diagram.png)\n",
	)

	body = renderer.render(item)

	assert_eq(body.html, '<p><img src="diagram.png" alt="A diagram"></p>\n')


def test_renders_image_alt_as_plain_text():
	renderer = Renderer(
		Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)]),
		Destinations(URLs([], URL.parse("https://example.com")), {}),
	)
	item = Item.markdown(
		ContentPath.parse("articles/intro"),
		"![A *simple* diagram &amp; `key`](diagram.png)\n",
	)

	body = renderer.render(item)

	assert_eq(
		body.html,
		'<p><img src="diagram.png" alt="A simple diagram &amp; key"></p>\n',
	)
