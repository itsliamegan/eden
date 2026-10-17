from luna.test.assertion import assert_eq, assert_raises

from eden.content import ContentError, ContentPath


def test_parses_segments():
	path = ContentPath.parse("guides/database/indexes")

	assert_eq(path.segments, ("guides", "database", "indexes"))


def test_names_path_by_last_segment():
	path = ContentPath.parse("articles/intro")

	assert_eq(path.name, "intro")


def test_gives_parent():
	path = ContentPath.parse("guides/database/indexes")

	assert_eq(path.parent, ContentPath.parse("guides/database"))


def test_gives_no_parent_at_top_of_content():
	path = ContentPath.parse("about")

	assert_eq(path.parent, None)


def test_prints_as_text():
	path = ContentPath.parse("articles/intro")

	assert_eq(str(path), "articles/intro")


def test_finds_entry_keyed_by_equal_path():
	orders = {ContentPath.parse("articles"): "date"}

	assert_eq(orders[ContentPath.parse("articles")], "date")


def test_rejects_empty_path():
	with assert_raises(ContentError):
		ContentPath.parse("")


def test_rejects_leading_slash():
	with assert_raises(ContentError):
		ContentPath.parse("/articles")


def test_rejects_trailing_slash():
	with assert_raises(ContentError):
		ContentPath.parse("articles/")


def test_rejects_empty_segment():
	with assert_raises(ContentError):
		ContentPath.parse("articles//intro")


def test_rejects_parent_segment():
	with assert_raises(ContentError):
		ContentPath.parse("articles/../about")


def test_rejects_current_segment():
	with assert_raises(ContentError):
		ContentPath.parse("./about")
