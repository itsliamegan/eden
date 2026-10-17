from luna.test.assertion import assert_eq

from eden.content import Collection, ContentPath, Item, Items


def test_iterates_items():
	first = Item(ContentPath.parse("writing/first"), {}, "")
	second = Item(ContentPath.parse("writing/second"), {}, "")
	collection = Collection(ContentPath.parse("writing"), Items([first, second]))

	assert_eq(list(collection), [first, second])


def test_sorts_items():
	first = Item(ContentPath.parse("writing/first"), {"position": 1}, "")
	second = Item(ContentPath.parse("writing/second"), {"position": 2}, "")
	collection = Collection(ContentPath.parse("writing"), Items([second, first]))

	assert_eq(collection.sort("position"), Items([first, second]))


def test_reverses_items():
	first = Item(ContentPath.parse("writing/first"), {}, "")
	second = Item(ContentPath.parse("writing/second"), {}, "")
	collection = Collection(ContentPath.parse("writing"), Items([first, second]))

	assert_eq(collection.reverse(), Items([second, first]))


def test_concats_collection():
	essay = Item(ContentPath.parse("writing/essay"), {}, "")
	link = Item(ContentPath.parse("links/link"), {}, "")
	writing = Collection(ContentPath.parse("writing"), Items([essay]))
	links = Collection(ContentPath.parse("links"), Items([link]))

	assert_eq(writing.concat(links), Items([essay, link]))
