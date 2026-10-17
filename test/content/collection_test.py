from luna.test.assertion import assert_eq

from eden.content import Collection, Item, Items


def test_iterates_items():
	first = Item("writing/first", {}, "")
	second = Item("writing/second", {}, "")
	collection = Collection("writing", Items([first, second]))

	assert_eq(list(collection), [first, second])


def test_sorts_items():
	first = Item("writing/first", {"position": 1}, "")
	second = Item("writing/second", {"position": 2}, "")
	collection = Collection("writing", Items([second, first]))

	assert_eq(collection.sort("position"), Items([first, second]))


def test_reverses_items():
	first = Item("writing/first", {}, "")
	second = Item("writing/second", {}, "")
	collection = Collection("writing", Items([first, second]))

	assert_eq(collection.reverse(), Items([second, first]))


def test_concats_collection():
	essay = Item("writing/essay", {}, "")
	link = Item("links/link", {}, "")
	writing = Collection("writing", Items([essay]))
	links = Collection("links", Items([link]))

	assert_eq(writing.concat(links), Items([essay, link]))
