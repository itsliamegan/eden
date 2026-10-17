from uuid import uuid4

from luna.test.assertion import assert_eq, assert_not_eq, assert_raises

from eden.content import ContentError, Item


def test_reads_front_matter_and_body():
	title = uuid4().hex
	item = Item.markdown("about", f'+++\ntitle = "{title}"\n+++\nFirst\n')

	assert_eq(item.fields, {"title": title})
	assert_eq(item.text, "First\n")


def test_reads_empty_front_matter():
	item = Item.markdown("about", "+++\n+++\nFirst\n")

	assert_eq(item.fields, {})
	assert_eq(item.text, "First\n")


def test_reads_body_without_front_matter():
	item = Item.markdown("about", "First\n")

	assert_eq(item.fields, {})
	assert_eq(item.text, "First\n")


def test_keeps_rule_in_body():
	item = Item.markdown("about", '+++\ntitle = "About"\n+++\nFirst\n\n---\nSecond\n')

	assert_eq(item.text, "First\n\n---\nSecond\n")


def test_keeps_delimiter_in_body():
	item = Item.markdown("about", "+++\n+++\nFirst\n+++\nSecond\n")

	assert_eq(item.text, "First\n+++\nSecond\n")


def test_reads_rule_at_start_as_body():
	item = Item.markdown("about", "---\ntitle = 1\n---\n")

	assert_eq(item.fields, {})
	assert_eq(item.text, "---\ntitle = 1\n---\n")


def test_rejects_unclosed_front_matter():
	with assert_raises(ContentError):
		Item.markdown("about", '+++\ntitle = "About"\n')


def test_reads_toml_fields():
	title = uuid4().hex
	item = Item.toml("info", f'title = "{title}"\n')

	assert_eq(item.fields, {"title": title})
	assert_eq(item.text, "")


def test_names_item_by_last_segment():
	name = uuid4().hex
	item = Item.toml(f"writing/{name}", "")

	assert_eq(item.name, name)


def test_gives_field():
	title = uuid4().hex
	item = Item.toml("about", f'title = "{title}"\n')

	assert_eq(item.field("title"), title)


def test_gives_nothing_for_unset_field():
	item = Item.toml("about", "")

	assert_eq(item.field("title"), None)


def test_equals_item_at_same_path():
	path = f"writing/{uuid4().hex}"

	assert_eq(Item.toml(path, "title = 1"), Item.toml(path, "title = 2"))


def test_differs_from_item_at_other_path():
	assert_not_eq(Item.toml(uuid4().hex, ""), Item.toml(uuid4().hex, ""))
