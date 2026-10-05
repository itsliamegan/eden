from eden.resource import Collection, Page, Site
from eden.template import Template
from eden.template.format import html


def test_titleizes_name():
	site = Site("blog")
	page = Page("about", metadata={}, template=empty_template(), container=site)

	assert page.title == "About"


def test_uses_custom_title():
	site = Site("blog")
	page = Page(
		"contact_us",
		metadata={"title": "Contact"},
		template=empty_template(),
		container=site,
	)

	assert page.title == "Contact"


def test_index_uses_container_title():
	site = Site("blog")
	page = Page("index", metadata={}, template=empty_template(), container=site)

	assert page.title == "Blog"


def test_joins_slug_to_container_permalink():
	site = Site("blog")
	page = Page("about", metadata={}, template=empty_template(), container=site)

	assert str(page.permalink) == "/about"


def test_joins_slug_to_collection_permalink():
	site = Site("blog")
	collection = Collection("articles", metadata={}, container=site)
	page = Page(
		"hello_world",
		metadata={},
		template=empty_template(),
		container=collection,
	)

	assert str(page.permalink) == "/articles/hello-world"


def test_accesses_metadata_attributes():
	site = Site("blog")
	collection = Collection("articles", metadata={}, container=site)
	page = Page(
		"hello_world",
		metadata={"author": "Liam Egan"},
		template=empty_template(),
		container=collection,
	)

	assert page.author == "Liam Egan"


def empty_template():
	return Template.compile("", html.Format())
