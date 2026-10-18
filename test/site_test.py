from helios.assets import Manifest
from helios.url import URL
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
