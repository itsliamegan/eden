from uuid import uuid4

from luna.test.assertion import assert_eq

from eden.content import Collection, Item, Items


def test_iterates_items():
	first = item()
	second = item()
	collection = Collection("writing", Items([first, second]))

	assert_eq(list(collection), [first, second])


def test_sorts_items():
	first = item(position=1)
	second = item(position=2)
	collection = Collection("writing", Items([second, first]))

	assert_eq(collection.sort("position"), Items([first, second]))


def test_reverses_items():
	first = item()
	second = item()
	collection = Collection("writing", Items([first, second]))

	assert_eq(collection.reverse(), Items([second, first]))


def test_concats_collection():
	first = item()
	second = item()
	writing = Collection("writing", Items([first]))
	links = Collection("links", Items([second]))

	assert_eq(writing.concat(links), Items([first, second]))


def item(**fields):
	return Item(f"writing/{uuid4().hex}", fields, "")
