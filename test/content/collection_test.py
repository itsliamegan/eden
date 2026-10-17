from luna.test.assertion import assert_eq

from eden.content import Collection, ContentPath, Item, Items


def test_iterates_items():
	first = Item(ContentPath.parse("articles/first"), {}, "")
	second = Item(ContentPath.parse("articles/second"), {}, "")
	collection = Collection(ContentPath.parse("articles"), Items([first, second]))

	assert_eq(list(collection), [first, second])


def test_sorts_items():
	first = Item(ContentPath.parse("articles/first"), {"position": 1}, "")
	second = Item(ContentPath.parse("articles/second"), {"position": 2}, "")
	collection = Collection(ContentPath.parse("articles"), Items([second, first]))

	assert_eq(collection.sort("position"), Items([first, second]))


def test_reverses_items():
	first = Item(ContentPath.parse("articles/first"), {}, "")
	second = Item(ContentPath.parse("articles/second"), {}, "")
	collection = Collection(ContentPath.parse("articles"), Items([first, second]))

	assert_eq(collection.reverse(), Items([second, first]))


def test_concats_collection():
	intro = Item(ContentPath.parse("articles/intro"), {}, "")
	link = Item(ContentPath.parse("links/link"), {}, "")
	articles = Collection(ContentPath.parse("articles"), Items([intro]))
	links = Collection(ContentPath.parse("links"), Items([link]))

	assert_eq(articles.concat(links), Items([intro, link]))
