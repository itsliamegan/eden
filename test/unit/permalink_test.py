from eden.permalink import Permalink


def test_creates_root():
	root = Permalink.root()

	assert root == Permalink([], is_index=True)


def test_joins_segment_to_index():
	index = Permalink(["articles"], is_index=True)
	entry = index.join("hello-world")

	assert entry == Permalink(["articles", "hello-world"])


def test_converts_entry_to_index():
	entry = Permalink(["articles"])
	index = entry.to_index()

	assert index == Permalink(["articles"], is_index=True)


def test_stringifies_root():
	root = Permalink.root()

	assert str(root) == "/"


def test_stringifies_index():
	index = Permalink(["articles"], is_index=True)

	assert str(index) == "/articles/"


def test_stringifies_entry():
	entry = Permalink(["about"])

	assert str(entry) == "/about"
