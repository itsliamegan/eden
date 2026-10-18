from helios.assets import Manifest
from helios.url import Pattern, URL
from luna.test.assertion import assert_eq, assert_is, assert_raises

from eden.config import Config
from eden.content import (
	Collection,
	ContentNotFoundError,
	ContentPath,
	Item,
	Items,
	Order,
)
from eden.driver import memory
from eden.markdown import MarkdownError
from eden.routing import Route
from eden.routing.route import PerItemExpansion
from eden.site import Site


def test_finds_top_level_item():
	about = Item(ContentPath.parse("about"), {}, "")
	site = Site.read(
		Config(URL.parse("https://example.com"), [], [], [], {}),
		Manifest({}, {}),
		memory.Driver(items=[about]),
	)

	assert_is(site.item("about"), about)


def test_finds_collection_item():
	intro = Item(ContentPath.parse("articles/intro"), {}, "")
	site = Site.read(
		Config(URL.parse("https://example.com"), [], [], [], {}),
		Manifest({}, {}),
		memory.Driver(
			collections=[Collection(ContentPath.parse("articles"), Items([intro]))],
		),
	)

	assert_is(site.item("articles/intro"), intro)


def test_finds_index_item():
	index = Item(ContentPath.parse("articles"), {}, "")
	site = Site.read(
		Config(URL.parse("https://example.com"), [], [], [], {}),
		Manifest({}, {}),
		memory.Driver(
			collections=[Collection(ContentPath.parse("articles"), Items([]), index)],
		),
	)

	assert_is(site.item("articles"), index)


def test_raises_on_missing_item():
	site = Site.read(
		Config(URL.parse("https://example.com"), [], [], [], {}),
		Manifest({}, {}),
		memory.Driver(),
	)

	with assert_raises(ContentNotFoundError):
		site.item("about")


def test_finds_collection():
	articles = Collection(ContentPath.parse("articles"), Items([]))
	site = Site.read(
		Config(URL.parse("https://example.com"), [], [], [], {}),
		Manifest({}, {}),
		memory.Driver(collections=[articles]),
	)

	assert_is(site.collection("articles"), articles)


def test_raises_on_missing_collection():
	site = Site.read(
		Config(URL.parse("https://example.com"), [], [], [], {}),
		Manifest({}, {}),
		memory.Driver(),
	)

	with assert_raises(ContentNotFoundError):
		site.collection("articles")


def test_sorts_collection_by_its_order():
	intro = Item(ContentPath.parse("articles/intro"), {"position": 1}, "")
	outro = Item(ContentPath.parse("articles/outro"), {"position": 2}, "")
	site = Site.read(
		Config(
			URL.parse("https://example.com"),
			[],
			[],
			[],
			{ContentPath.parse("articles"): Order("position", "asc")},
		),
		Manifest({}, {}),
		memory.Driver(
			collections=[
				Collection(ContentPath.parse("articles"), Items([outro, intro])),
			],
		),
	)

	assert_eq(list(site.collection("articles")), [intro, outro])


def test_sorts_collection_in_descending_order():
	intro = Item(ContentPath.parse("articles/intro"), {"position": 1}, "")
	outro = Item(ContentPath.parse("articles/outro"), {"position": 2}, "")
	site = Site.read(
		Config(
			URL.parse("https://example.com"),
			[],
			[],
			[],
			{ContentPath.parse("articles"): Order("position", "desc")},
		),
		Manifest({}, {}),
		memory.Driver(
			collections=[
				Collection(ContentPath.parse("articles"), Items([intro, outro])),
			],
		),
	)

	assert_eq(list(site.collection("articles")), [outro, intro])


def test_keeps_index_item_of_sorted_collection():
	index = Item(ContentPath.parse("articles"), {}, "")
	site = Site.read(
		Config(
			URL.parse("https://example.com"),
			[],
			[],
			[],
			{ContentPath.parse("articles"): Order("position", "asc")},
		),
		Manifest({}, {}),
		memory.Driver(
			collections=[Collection(ContentPath.parse("articles"), Items([]), index)],
		),
	)

	assert_is(site.item("articles"), index)


def test_raises_on_order_for_missing_collection():
	config = Config(
		URL.parse("https://example.com"),
		[],
		[],
		[],
		{ContentPath.parse("articles"): Order("position", "asc")},
	)

	with assert_raises(ContentNotFoundError):
		Site.read(config, Manifest({}, {}), memory.Driver())


def test_renders_item_bodies():
	intro = Item.markdown(ContentPath.parse("articles/intro"), "Read *this* first.\n")
	Site.read(
		Config(URL.parse("https://example.com"), [], [], [], {}),
		Manifest({}, {}),
		memory.Driver(
			collections=[Collection(ContentPath.parse("articles"), Items([intro]))],
		),
	)

	assert_eq(intro.body, "<p>Read <em>this</em> first.</p>\n")


def test_collects_item_headings():
	intro = Item.markdown(ContentPath.parse("articles/intro"), "# Setup\n")
	Site.read(
		Config(URL.parse("https://example.com"), [], [], [], {}),
		Manifest({}, {}),
		memory.Driver(
			collections=[Collection(ContentPath.parse("articles"), Items([intro]))],
		),
	)

	assert intro.headings is not None
	assert_eq(intro.headings[0].id, "setup")


def test_links_items_by_their_pages():
	intro = Item.markdown(ContentPath.parse("articles/intro"), "[Outro](outro.md)\n")
	outro = Item.markdown(ContentPath.parse("articles/outro"), "")
	route = Route(
		"article",
		Pattern.parse("/articles/{name}"),
		"articles/show",
		PerItemExpansion(ContentPath.parse("articles")),
	)
	Site.read(
		Config(URL.parse("https://example.com"), [], [], [route], {}),
		Manifest({}, {}),
		memory.Driver(
			collections=[
				Collection(ContentPath.parse("articles"), Items([intro, outro])),
			],
		),
	)

	assert_eq(intro.body, '<p><a href="/articles/outro">Outro</a></p>\n')


def test_renders_bodies_through_site_component_templates():
	intro = Item.markdown(ContentPath.parse("articles/intro"), "[Manual](/manual)\n")
	Site.read(
		Config(URL.parse("https://example.com"), [], [], [], {}),
		Manifest({}, {}),
		memory.Driver(
			collections=[Collection(ContentPath.parse("articles"), Items([intro]))],
			views={
				"components/markdown/link": (
					'<a class="link" href="{{ href }}">{{ content }}</a>'
				),
			},
		),
	)

	assert_eq(intro.body, '<p><a class="link" href="/manual">Manual</a></p>\n')


def test_raises_on_body_linking_to_missing_item():
	intro = Item.markdown(ContentPath.parse("articles/intro"), "[Outro](outro.md)\n")
	config = Config(URL.parse("https://example.com"), [], [], [], {})
	driver = memory.Driver(
		collections=[Collection(ContentPath.parse("articles"), Items([intro]))],
	)

	with assert_raises(MarkdownError):
		Site.read(config, Manifest({}, {}), driver)
