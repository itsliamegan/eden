from eden.resource import Collection, Page, Site


def test_titleizes_name():
	site = Site("blog")
	collection = Collection("articles", metadata={}, container=site)

	assert collection.title == "Articles"


def test_uses_custom_title():
	site = Site("blog")
	collection = Collection("articles", metadata={"title": "Writing"}, container=site)

	assert collection.title == "Writing"


def test_iterates_content():
	site = Site("blog")
	collection = Collection("articles", metadata={}, container=site)
	page = Page("hello_world", metadata={}, template=None, container=collection)
	collection.add_content(page)

	assert list(collection) == [page]


def test_iterates_content_in_order():
	site = Site("blog")
	collection = Collection(
		"articles",
		metadata={"sort": {"attr": "order", "order": "ascending"}},
		container=site,
	)
	first_page = Page(
		"first_page", metadata={"order": 1}, template=None, container=collection
	)
	second_page = Page(
		"second_page", metadata={"order": 2}, template=None, container=collection
	)
	collection.add_content(second_page)
	collection.add_content(first_page)

	assert list(collection) == [first_page, second_page]
