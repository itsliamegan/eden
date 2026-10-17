from luna.test.assertion import assert_eq, assert_raises

from eden.content import ContentError, ContentPath, Item, Items


def test_iterates_in_order():
	first = Item(ContentPath.parse("articles/first"), {}, "")
	second = Item(ContentPath.parse("articles/second"), {}, "")
	items = Items([first, second])

	assert_eq(list(items), [first, second])


def test_sorts_by_field():
	first = Item(ContentPath.parse("articles/first"), {"position": 1}, "")
	second = Item(ContentPath.parse("articles/second"), {"position": 2}, "")
	items = Items([second, first])

	assert_eq(items.sort("position"), Items([first, second]))


def test_keeps_order_of_equal_values():
	first = Item(ContentPath.parse("articles/first"), {"position": 1}, "")
	second = Item(ContentPath.parse("articles/second"), {"position": 1}, "")
	items = Items([first, second])

	assert_eq(items.sort("position"), Items([first, second]))


def test_rejects_sort_by_unset_field():
	first = Item(ContentPath.parse("articles/first"), {"position": 1}, "")
	second = Item(ContentPath.parse("articles/second"), {}, "")
	items = Items([first, second])

	with assert_raises(ContentError):
		items.sort("position")


def test_rejects_sort_by_values_that_cannot_be_compared():
	first = Item(ContentPath.parse("articles/first"), {"position": 1}, "")
	second = Item(ContentPath.parse("articles/second"), {"position": "second"}, "")
	items = Items([first, second])

	with assert_raises(ContentError):
		items.sort("position")


def test_reverses():
	first = Item(ContentPath.parse("articles/first"), {}, "")
	second = Item(ContentPath.parse("articles/second"), {}, "")
	items = Items([first, second])

	assert_eq(items.reverse(), Items([second, first]))


def test_concats_items():
	first = Item(ContentPath.parse("articles/first"), {}, "")
	second = Item(ContentPath.parse("articles/second"), {}, "")

	assert_eq(Items([first]).concat(Items([second])), Items([first, second]))


def test_leaves_items_unchanged():
	first = Item(ContentPath.parse("articles/first"), {"position": 2}, "")
	second = Item(ContentPath.parse("articles/second"), {"position": 1}, "")
	third = Item(ContentPath.parse("articles/third"), {}, "")
	items = Items([first, second])

	items.sort("position")
	items.reverse()
	items.concat(Items([third]))

	assert_eq(items, Items([first, second]))
