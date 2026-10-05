from luna.test.assertion import assert_eq, assert_raises

from eden.resource import Collection, Page, Site
from eden.template import Template
from eden.template.format import html


def test_titleizes_name():
	site = Site("blog")
	collection = Collection("articles", metadata={}, container=site)

	assert_eq(collection.title, "Articles")


def test_uses_custom_title():
	site = Site("blog")
	collection = Collection("articles", metadata={"title": "Writing"}, container=site)

	assert_eq(collection.title, "Writing")


def test_joins_slug_to_container_permalink_as_index():
	site = Site("blog")
	collection = Collection("hello_world", metadata={}, container=site)

	assert_eq(str(collection.permalink), "/hello-world/")


def test_iterates_content():
	site = Site("blog")
	collection = Collection("articles", metadata={}, container=site)
	page = Page.entry(
		"hello_world",
		metadata={},
		template=empty_template(),
		container=collection,
	)
	collection.add_content(page)

	assert_eq(list(collection), [page])


def test_excludes_index_from_content():
	site = Site("blog")
	collection = Collection("articles", metadata={}, container=site)
	index = Page.index(
		"articles",
		metadata={},
		template=empty_template(),
		container=collection,
	)
	page = Page.entry(
		"hello_world",
		metadata={},
		template=empty_template(),
		container=collection,
	)
	collection.index = index
	collection.add_content(page)

	assert_eq(list(collection), [page])


def test_iterates_content_in_order():
	site = Site("blog")
	collection = Collection(
		"articles",
		metadata={"sort": {"attr": "order", "order": "ascending"}},
		container=site,
	)
	first_page = Page.entry(
		"first_page",
		metadata={"order": 1},
		template=empty_template(),
		container=collection,
	)
	second_page = Page.entry(
		"second_page",
		metadata={"order": 2},
		template=empty_template(),
		container=collection,
	)
	collection.add_content(second_page)
	collection.add_content(first_page)

	assert_eq(list(collection), [first_page, second_page])


def test_rejects_unknown_sort_order():
	site = Site("blog")

	with assert_raises(ValueError):
		Collection(
			"articles",
			metadata={"sort": {"attr": "order", "order": "sideways"}},
			container=site,
		)


def empty_template():
	return Template.compile("", html.Format())
