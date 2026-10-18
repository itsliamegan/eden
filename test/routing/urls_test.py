from helios.url import Pattern, URL
from luna.test.assertion import assert_eq, assert_raises

from eden.content import ContentPath, Item
from eden.routing import (
	Route,
	RouteError,
	RouteNotFoundError,
	URLs,
)
from eden.routing.route import PerItemExpansion, SingleExpansion


def test_builds_per_item_route_url():
	route = Route(
		"article",
		Pattern.parse("/articles/{name}"),
		"articles/show",
		PerItemExpansion(ContentPath.parse("articles")),
	)
	urls = URLs([route], URL.parse("https://example.com"))

	url = urls.route("article", Item(ContentPath.parse("articles/intro"), {}, ""))

	assert_eq(str(url), "/articles/intro")


def test_builds_single_path_url():
	route = Route(
		"about",
		Pattern.parse("/about"),
		"page",
		SingleExpansion(ContentPath.parse("about")),
	)
	urls = URLs([route], URL.parse("https://example.com"))

	url = urls.route("about")

	assert_eq(str(url), "/about")


def test_builds_absolute_route_url():
	route = Route(
		"article",
		Pattern.parse("/articles/{name}"),
		"articles/show",
		PerItemExpansion(ContentPath.parse("articles")),
	)
	urls = URLs([route], URL.parse("https://example.com:8443"))

	url = urls.route(
		"article", Item(ContentPath.parse("articles/intro"), {}, ""), absolute=True
	)

	assert_eq(str(url), "https://example.com:8443/articles/intro")


def test_prefixes_route_url_with_base_url_path():
	route = Route(
		"article",
		Pattern.parse("/articles/{name}"),
		"articles/show",
		PerItemExpansion(ContentPath.parse("articles")),
	)
	urls = URLs([route], URL.parse("https://example.com/mesa"))

	url = urls.route("article", Item(ContentPath.parse("articles/intro"), {}, ""))

	assert_eq(str(url), "/mesa/articles/intro")


def test_keeps_trailing_slash_of_root_under_base_url_path():
	route = Route("home", Pattern.parse("/"), "home", SingleExpansion(None))
	urls = URLs([route], URL.parse("https://example.com/mesa"))

	url = urls.route("home")

	assert_eq(str(url), "/mesa/")


def test_ignores_trailing_slash_on_base_url():
	route = Route(
		"about",
		Pattern.parse("/about"),
		"page",
		SingleExpansion(ContentPath.parse("about")),
	)
	urls = URLs([route], URL.parse("https://example.com/mesa/"))

	url = urls.route("about")

	assert_eq(str(url), "/mesa/about")


def test_builds_root_url_without_base_url_path():
	route = Route("home", Pattern.parse("/"), "home", SingleExpansion(None))
	urls = URLs([route], URL.parse("https://example.com"))

	url = urls.route("home")

	assert_eq(str(url), "/")


def test_rejects_unknown_route_name():
	route = Route(
		"about",
		Pattern.parse("/about"),
		"page",
		SingleExpansion(ContentPath.parse("about")),
	)
	urls = URLs([route], URL.parse("https://example.com"))

	with assert_raises(RouteNotFoundError):
		urls.route("contact")


def test_rejects_item_for_single_path():
	route = Route(
		"about",
		Pattern.parse("/about"),
		"page",
		SingleExpansion(ContentPath.parse("about")),
	)
	urls = URLs([route], URL.parse("https://example.com"))

	with assert_raises(RouteError):
		urls.route("about", Item(ContentPath.parse("about"), {}, ""))


def test_rejects_per_item_route_without_item():
	route = Route(
		"article",
		Pattern.parse("/articles/{name}"),
		"articles/show",
		PerItemExpansion(ContentPath.parse("articles")),
	)
	urls = URLs([route], URL.parse("https://example.com"))

	with assert_raises(RouteError):
		urls.route("article")


def test_rejects_item_from_other_collection():
	route = Route(
		"article",
		Pattern.parse("/articles/{name}"),
		"articles/show",
		PerItemExpansion(ContentPath.parse("articles")),
	)
	urls = URLs([route], URL.parse("https://example.com"))

	with assert_raises(RouteError):
		urls.route("article", Item(ContentPath.parse("links/intro"), {}, ""))


def test_builds_item_url_from_per_item_route():
	route = Route(
		"article",
		Pattern.parse("/articles/{name}"),
		"articles/show",
		PerItemExpansion(ContentPath.parse("articles")),
	)
	urls = URLs([route], URL.parse("https://example.com"))

	url = urls.item(Item(ContentPath.parse("articles/intro"), {}, ""))

	assert_eq(str(url), "/articles/intro")


def test_builds_item_url_from_single_route():
	route = Route(
		"about",
		Pattern.parse("/about"),
		"page",
		SingleExpansion(ContentPath.parse("about")),
	)
	urls = URLs([route], URL.parse("https://example.com"))

	url = urls.item(Item(ContentPath.parse("about"), {}, ""))

	assert_eq(str(url), "/about")


def test_builds_item_url_from_unnamed_route():
	route = Route(
		None,
		Pattern.parse("/articles/{name}"),
		"articles/show",
		PerItemExpansion(ContentPath.parse("articles")),
	)
	urls = URLs([route], URL.parse("https://example.com"))

	url = urls.item(Item(ContentPath.parse("articles/intro"), {}, ""))

	assert_eq(str(url), "/articles/intro")


def test_prefixes_item_url_with_base_url_path():
	route = Route(
		"article",
		Pattern.parse("/articles/{name}"),
		"articles/show",
		PerItemExpansion(ContentPath.parse("articles")),
	)
	urls = URLs([route], URL.parse("https://example.com/mesa"))

	url = urls.item(Item(ContentPath.parse("articles/intro"), {}, ""))

	assert_eq(str(url), "/mesa/articles/intro")


def test_builds_absolute_item_url():
	route = Route(
		"article",
		Pattern.parse("/articles/{name}"),
		"articles/show",
		PerItemExpansion(ContentPath.parse("articles")),
	)
	urls = URLs([route], URL.parse("https://example.com:8443"))

	url = urls.item(Item(ContentPath.parse("articles/intro"), {}, ""), absolute=True)

	assert_eq(str(url), "https://example.com:8443/articles/intro")


def test_rejects_item_no_route_renders():
	route = Route(
		"article",
		Pattern.parse("/articles/{name}"),
		"articles/show",
		PerItemExpansion(ContentPath.parse("articles")),
	)
	urls = URLs([route], URL.parse("https://example.com"))

	with assert_raises(RouteNotFoundError):
		urls.item(Item(ContentPath.parse("about"), {}, ""))


def test_leaves_index_item_out_of_per_item_route():
	route = Route(
		"article",
		Pattern.parse("/articles/{name}"),
		"articles/show",
		PerItemExpansion(ContentPath.parse("articles")),
	)
	urls = URLs([route], URL.parse("https://example.com"))

	with assert_raises(RouteNotFoundError):
		urls.item(Item(ContentPath.parse("articles"), {}, ""))


def test_builds_path_url():
	urls = URLs([], URL.parse("https://example.com/mesa"))

	url = urls.path("/favicon.png")

	assert_eq(str(url), "/mesa/favicon.png")


def test_builds_absolute_path_url():
	urls = URLs([], URL.parse("https://example.com/mesa"))

	url = urls.path("/articles/", absolute=True)

	assert_eq(str(url), "https://example.com/mesa/articles/")
