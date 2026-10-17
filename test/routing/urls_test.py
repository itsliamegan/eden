from helios.url import Pattern, URL
from luna.test.assertion import assert_eq, assert_raises

from eden.content import ContentPath, Item
from eden.routing import (
	PerItemExpansion,
	Route,
	RouteError,
	RouteNotFoundError,
	SingleExpansion,
	URLs,
)


def test_builds_per_item_route_url():
	route = Route(
		"essay",
		Pattern.parse("/writing/{name}"),
		"writing/show",
		PerItemExpansion(ContentPath.parse("writing")),
	)
	urls = URLs([route], URL.parse("https://example.com"))

	url = urls.route("essay", Item(ContentPath.parse("writing/tranquility"), {}, ""))

	assert_eq(str(url), "/writing/tranquility")


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
		"essay",
		Pattern.parse("/writing/{name}"),
		"writing/show",
		PerItemExpansion(ContentPath.parse("writing")),
	)
	urls = URLs([route], URL.parse("https://example.com:8443"))

	url = urls.route(
		"essay", Item(ContentPath.parse("writing/tranquility"), {}, ""), absolute=True
	)

	assert_eq(str(url), "https://example.com:8443/writing/tranquility")


def test_prefixes_route_url_with_base_url_path():
	route = Route(
		"essay",
		Pattern.parse("/writing/{name}"),
		"writing/show",
		PerItemExpansion(ContentPath.parse("writing")),
	)
	urls = URLs([route], URL.parse("https://example.com/mesa"))

	url = urls.route("essay", Item(ContentPath.parse("writing/tranquility"), {}, ""))

	assert_eq(str(url), "/mesa/writing/tranquility")


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
		"essay",
		Pattern.parse("/writing/{name}"),
		"writing/show",
		PerItemExpansion(ContentPath.parse("writing")),
	)
	urls = URLs([route], URL.parse("https://example.com"))

	with assert_raises(RouteError):
		urls.route("essay")


def test_rejects_item_from_other_collection():
	route = Route(
		"essay",
		Pattern.parse("/writing/{name}"),
		"writing/show",
		PerItemExpansion(ContentPath.parse("writing")),
	)
	urls = URLs([route], URL.parse("https://example.com"))

	with assert_raises(RouteError):
		urls.route("essay", Item(ContentPath.parse("links/tranquility"), {}, ""))


def test_builds_path_url():
	urls = URLs([], URL.parse("https://example.com/mesa"))

	url = urls.path("/favicon.png")

	assert_eq(str(url), "/mesa/favicon.png")


def test_builds_absolute_path_url():
	urls = URLs([], URL.parse("https://example.com/mesa"))

	url = urls.path("/writing/", absolute=True)

	assert_eq(str(url), "https://example.com/mesa/writing/")
