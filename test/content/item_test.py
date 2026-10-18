from luna.test.assertion import assert_eq, assert_not_eq, assert_raises

from eden.content import ContentError, ContentPath, Item


def test_reads_front_matter_and_body():
	item = Item.markdown(
		ContentPath.parse("about"), '+++\ntitle = "About"\n+++\nFirst\n'
	)

	assert_eq(item.fields, {"title": "About"})
	assert_eq(item.text, "First\n")


def test_reads_empty_front_matter():
	item = Item.markdown(ContentPath.parse("about"), "+++\n+++\nFirst\n")

	assert_eq(item.fields, {})
	assert_eq(item.text, "First\n")


def test_reads_body_without_front_matter():
	item = Item.markdown(ContentPath.parse("about"), "First\n")

	assert_eq(item.fields, {})
	assert_eq(item.text, "First\n")


def test_keeps_rule_in_body():
	item = Item.markdown(
		ContentPath.parse("about"), '+++\ntitle = "About"\n+++\nFirst\n\n---\nSecond\n'
	)

	assert_eq(item.text, "First\n\n---\nSecond\n")


def test_keeps_delimiter_in_body():
	item = Item.markdown(ContentPath.parse("about"), "+++\n+++\nFirst\n+++\nSecond\n")

	assert_eq(item.text, "First\n+++\nSecond\n")


def test_reads_rule_at_start_as_body():
	item = Item.markdown(ContentPath.parse("about"), "---\ntitle = 1\n---\n")

	assert_eq(item.fields, {})
	assert_eq(item.text, "---\ntitle = 1\n---\n")


def test_rejects_unclosed_front_matter():
	with assert_raises(ContentError):
		Item.markdown(ContentPath.parse("about"), '+++\ntitle = "About"\n')


def test_rejects_invalid_front_matter():
	with assert_raises(ContentError):
		Item.markdown(ContentPath.parse("about"), "+++\ntitle =\n+++\nFirst\n")


def test_reads_toml_fields():
	item = Item.toml(ContentPath.parse("info"), 'title = "Liam Egan"\n')

	assert_eq(item.fields, {"title": "Liam Egan"})
	assert_eq(item.text, "")


def test_names_item_by_last_segment():
	item = Item.toml(ContentPath.parse("articles/intro"), "")

	assert_eq(item.name, "intro")


def test_gives_field():
	item = Item.toml(ContentPath.parse("about"), 'title = "About"\n')

	assert_eq(item.field("title"), "About")


def test_rejects_invalid_toml():
	with assert_raises(ContentError):
		Item.toml(ContentPath.parse("info"), "title =")


def test_gives_nothing_for_unset_field():
	item = Item.toml(ContentPath.parse("about"), "")

	assert_eq(item.field("title"), None)


def test_equals_item_at_same_path():
	first = Item.toml(ContentPath.parse("articles/intro"), "title = 1")
	second = Item.toml(ContentPath.parse("articles/intro"), "title = 2")

	assert_eq(first, second)


def test_differs_from_item_at_other_path():
	first = Item.toml(ContentPath.parse("articles/intro"), "")
	second = Item.toml(ContentPath.parse("articles/outro"), "")

	assert_not_eq(first, second)
