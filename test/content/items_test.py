from uuid import uuid4

from luna.test.assertion import assert_eq, assert_raises

from eden.content import ContentError, Item, Items


def test_iterates_in_order():
	first = item()
	second = item()
	items = Items([first, second])

	assert_eq(list(items), [first, second])


def test_sorts_by_field():
	first = item(position=1)
	second = item(position=2)
	items = Items([second, first])

	assert_eq(items.sort("position"), Items([first, second]))


def test_keeps_order_of_equal_values():
	first = item(position=1)
	second = item(position=1)
	items = Items([first, second])

	assert_eq(items.sort("position"), Items([first, second]))


def test_rejects_sort_by_unset_field():
	items = Items([item(position=1), item()])

	with assert_raises(ContentError):
		items.sort("position")


def test_rejects_sort_by_values_that_cannot_be_compared():
	items = Items([item(position=1), item(position="first")])

	with assert_raises(ContentError):
		items.sort("position")


def test_reverses():
	first = item()
	second = item()
	items = Items([first, second])

	assert_eq(items.reverse(), Items([second, first]))


def test_concats_items():
	first = item()
	second = item()

	assert_eq(Items([first]).concat(Items([second])), Items([first, second]))


def test_leaves_items_unchanged():
	first = item(position=2)
	second = item(position=1)
	items = Items([first, second])

	items.sort("position")
	items.reverse()
	items.concat(Items([item()]))

	assert_eq(items, Items([first, second]))


def item(**fields):
	return Item(f"writing/{uuid4().hex}", fields, "")
