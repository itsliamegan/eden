from luna.test.assertion import assert_eq

from eden.permalink import Permalink


def test_creates_root():
	root = Permalink.root()

	assert_eq(root, Permalink([], is_index=True))


def test_joins_segment_to_index():
	index = Permalink(["articles"], is_index=True)
	entry = index.join("hello-world")

	assert_eq(entry, Permalink(["articles", "hello-world"]))


def test_converts_entry_to_index():
	entry = Permalink(["articles"])
	index = entry.to_index()

	assert_eq(index, Permalink(["articles"], is_index=True))


def test_stringifies_root():
	root = Permalink.root()

	assert_eq(str(root), "/")


def test_stringifies_index():
	index = Permalink(["articles"], is_index=True)

	assert_eq(str(index), "/articles/")


def test_stringifies_entry():
	entry = Permalink(["about"])

	assert_eq(str(entry), "/about")
