from helios.url import Pattern, URL
from luna.test.assertion import assert_eq, assert_raises

from eden.content import ContentPath, Item
from eden.markdown import Destinations, MarkdownError
from eden.routing import Route, URLs
from eden.routing.route import PerItemExpansion, SingleExpansion


def test_passes_absolute_url_through():
	destinations = Destinations(URLs([], URL.parse("https://example.com")), {})
	item = Item(ContentPath.parse("articles/intro"), {}, "")

	href = destinations.link("https://example.org/manual?page=2", item)

	assert_eq(href, "https://example.org/manual?page=2")


def test_passes_other_scheme_through():
	destinations = Destinations(URLs([], URL.parse("https://example.com")), {})
	item = Item(ContentPath.parse("articles/intro"), {}, "")

	href = destinations.link("mailto:intro@example.com", item)

	assert_eq(href, "mailto:intro@example.com")


def test_passes_scheme_relative_url_through():
	destinations = Destinations(URLs([], URL.parse("https://example.com")), {})
	item = Item(ContentPath.parse("articles/intro"), {}, "")

	href = destinations.link("//cdn.example.org/manual.pdf", item)

	assert_eq(href, "//cdn.example.org/manual.pdf")


def test_passes_fragment_through():
	destinations = Destinations(URLs([], URL.parse("https://example.com/mesa")), {})
	item = Item(ContentPath.parse("articles/intro"), {}, "")

	href = destinations.link("#setup", item)

	assert_eq(href, "#setup")


def test_passes_relative_file_through():
	destinations = Destinations(URLs([], URL.parse("https://example.com/mesa")), {})
	item = Item(ContentPath.parse("articles/intro"), {}, "")

	href = destinations.link("slides.pdf", item)

	assert_eq(href, "slides.pdf")


def test_resolves_entities():
	destinations = Destinations(URLs([], URL.parse("https://example.com")), {})
	item = Item(ContentPath.parse("articles/intro"), {}, "")

	href = destinations.link("slides.pdf?part=1&amp;page=2", item)

	assert_eq(href, "slides.pdf?part=1&page=2")


def test_encodes_destination():
	destinations = Destinations(URLs([], URL.parse("https://example.com")), {})
	item = Item(ContentPath.parse("articles/intro"), {}, "")

	href = destinations.link("intro slides.pdf", item)

	assert_eq(href, "intro%20slides.pdf")


def test_builds_url_for_path():
	destinations = Destinations(URLs([], URL.parse("https://example.com/mesa")), {})
	item = Item(ContentPath.parse("articles/intro"), {}, "")

	href = destinations.link("/about", item)

	assert_eq(href, "/mesa/about")


def test_keeps_query_and_fragment_of_path():
	destinations = Destinations(URLs([], URL.parse("https://example.com/mesa")), {})
	item = Item(ContentPath.parse("articles/intro"), {}, "")

	href = destinations.link("/about?view=all#team", item)

	assert_eq(href, "/mesa/about?view=all#team")


def test_builds_url_for_linked_item():
	route = Route(
		"article",
		Pattern.parse("/articles/{name}"),
		"articles/show",
		PerItemExpansion(ContentPath.parse("articles")),
	)
	outro = Item(ContentPath.parse("articles/outro"), {}, "")
	destinations = Destinations(
		URLs([route], URL.parse("https://example.com/mesa")),
		{outro.path: outro},
	)
	item = Item(ContentPath.parse("articles/intro"), {}, "")

	href = destinations.link("outro.md", item)

	assert_eq(href, "/mesa/articles/outro")


def test_resolves_linked_item_against_item_path():
	route = Route(
		"about",
		Pattern.parse("/about"),
		"page",
		SingleExpansion(ContentPath.parse("about")),
	)
	about = Item(ContentPath.parse("about"), {}, "")
	destinations = Destinations(
		URLs([route], URL.parse("https://example.com")),
		{about.path: about},
	)
	item = Item(ContentPath.parse("articles/intro"), {}, "")

	href = destinations.link("../about.md", item)

	assert_eq(href, "/about")


def test_keeps_fragment_of_linked_item():
	route = Route(
		"article",
		Pattern.parse("/articles/{name}"),
		"articles/show",
		PerItemExpansion(ContentPath.parse("articles")),
	)
	outro = Item(ContentPath.parse("articles/outro"), {}, "")
	destinations = Destinations(
		URLs([route], URL.parse("https://example.com")),
		{outro.path: outro},
	)
	item = Item(ContentPath.parse("articles/intro"), {}, "")

	href = destinations.link("outro.md#setup", item)

	assert_eq(href, "/articles/outro#setup")


def test_rejects_link_to_file_that_is_not_item():
	destinations = Destinations(URLs([], URL.parse("https://example.com")), {})
	item = Item(ContentPath.parse("articles/intro"), {}, "")

	with assert_raises(MarkdownError):
		destinations.link("outro.md", item)


def test_rejects_link_to_item_without_page():
	outro = Item(ContentPath.parse("articles/outro"), {}, "")
	destinations = Destinations(
		URLs([], URL.parse("https://example.com")),
		{outro.path: outro},
	)
	item = Item(ContentPath.parse("articles/intro"), {}, "")

	with assert_raises(MarkdownError):
		destinations.link("outro.md", item)


def test_builds_url_for_image_path():
	destinations = Destinations(URLs([], URL.parse("https://example.com/mesa")), {})

	src = destinations.image("/diagram.png")

	assert_eq(src, "/mesa/diagram.png")


def test_passes_image_of_markdown_file_through():
	destinations = Destinations(URLs([], URL.parse("https://example.com")), {})

	src = destinations.image("outro.md")

	assert_eq(src, "outro.md")
