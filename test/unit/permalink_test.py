from eden.permalink import Kind, Permalink


def test_creates_root():
	root = Permalink.root()

	assert root == Permalink(Kind.INDEX, [])


def test_joins_component_to_index():
	index = Permalink(Kind.INDEX, ["articles"])
	entry = index.join("hello-world")

	assert entry == Permalink(Kind.ENTRY, ["articles", "hello-world"])


def test_converts_entry_to_index():
	entry = Permalink(Kind.ENTRY, ["articles"])
	index = entry.to_index()

	assert index == Permalink(Kind.INDEX, ["articles"])


def test_stringifies_root():
	root = Permalink.root()

	assert str(root) == "/"


def test_stringifies_index():
	index = Permalink(Kind.INDEX, ["articles"])

	assert str(index) == "/articles/"


def test_stringifies_entry():
	index = Permalink(Kind.ENTRY, ["about"])

	assert str(index) == "/about"
