from luna.test.assertion import assert_eq, assert_raises

from eden.content import ContentError, Item, Items


def test_iterates_in_order():
	first = Item("writing/first", {}, "")
	second = Item("writing/second", {}, "")
	items = Items([first, second])

	assert_eq(list(items), [first, second])


def test_sorts_by_field():
	first = Item("writing/first", {"position": 1}, "")
	second = Item("writing/second", {"position": 2}, "")
	items = Items([second, first])

	assert_eq(items.sort("position"), Items([first, second]))


def test_keeps_order_of_equal_values():
	first = Item("writing/first", {"position": 1}, "")
	second = Item("writing/second", {"position": 1}, "")
	items = Items([first, second])

	assert_eq(items.sort("position"), Items([first, second]))


def test_rejects_sort_by_unset_field():
	first = Item("writing/first", {"position": 1}, "")
	second = Item("writing/second", {}, "")
	items = Items([first, second])

	with assert_raises(ContentError):
		items.sort("position")


def test_rejects_sort_by_values_that_cannot_be_compared():
	first = Item("writing/first", {"position": 1}, "")
	second = Item("writing/second", {"position": "second"}, "")
	items = Items([first, second])

	with assert_raises(ContentError):
		items.sort("position")


def test_reverses():
	first = Item("writing/first", {}, "")
	second = Item("writing/second", {}, "")
	items = Items([first, second])

	assert_eq(items.reverse(), Items([second, first]))


def test_concats_items():
	first = Item("writing/first", {}, "")
	second = Item("writing/second", {}, "")

	assert_eq(Items([first]).concat(Items([second])), Items([first, second]))


def test_leaves_items_unchanged():
	first = Item("writing/first", {"position": 2}, "")
	second = Item("writing/second", {"position": 1}, "")
	third = Item("writing/third", {}, "")
	items = Items([first, second])

	items.sort("position")
	items.reverse()
	items.concat(Items([third]))

	assert_eq(items, Items([first, second]))
