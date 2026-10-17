from helios.url import Pattern
from luna.test.assertion import assert_eq, assert_raises

from eden.config import Config, ConfigError
from eden.content import ContentPath, Order
from eden.routing import Route
from eden.routing.route import PerItemExpansion, SingleExpansion


def test_reads_base_url():
	config = Config.parse('url = "https://example.com/mesa"')

	assert_eq(str(config.base_url), "https://example.com/mesa")


def test_defaults_base_url_to_local_address():
	config = Config.parse("")

	assert_eq(str(config.base_url), "http://localhost:3000")


def test_rejects_relative_base_url():
	with assert_raises(ConfigError):
		Config.parse('url = "/mesa"')


def test_reads_entry_points():
	config = Config.parse('[assets]\nscripts = ["main"]\nstyles = ["article"]')

	assert_eq(config.scripts, ["main"])
	assert_eq(config.styles, ["article"])


def test_defaults_entry_points_to_none():
	config = Config.parse("")

	assert_eq(config.scripts, [])
	assert_eq(config.styles, [])


def test_reads_per_item_route():
	config = Config.parse(
		'[[routes]]\nname = "article"\npath = "/articles/{name}.xml"\n'
		'view = "articles/show"\ncollection = "articles"'
	)

	assert_eq(
		config.routes,
		[
			Route(
				"article",
				Pattern.parse("/articles/{name}.xml"),
				"articles/show",
				PerItemExpansion(ContentPath.parse("articles")),
			),
		],
	)


def test_reads_single_path_route():
	config = Config.parse(
		'[[routes]]\nname = "guide"\npath = "/guide/"\nview = "page"\n'
		'item = "guides/database"'
	)

	assert_eq(
		config.routes,
		[
			Route(
				"guide",
				Pattern.parse("/guide/"),
				"page",
				SingleExpansion(ContentPath.parse("guides/database")),
			)
		],
	)


def test_reads_route_without_name_or_item():
	config = Config.parse('[[routes]]\npath = "/"\nview = "home"')

	assert_eq(
		config.routes, [Route(None, Pattern.parse("/"), "home", SingleExpansion(None))]
	)


def test_reads_collection_order():
	config = Config.parse(
		'[collections."guides/database"]\nsort = "date"\norder = "desc"'
	)

	assert_eq(
		config.orders, {ContentPath.parse("guides/database"): Order("date", "desc")}
	)


def test_defaults_collection_order_to_ascending():
	config = Config.parse('[collections.articles]\nsort = "position"')

	assert_eq(config.orders, {ContentPath.parse("articles"): Order("position", "asc")})


def test_rejects_invalid_toml():
	with assert_raises(ConfigError):
		Config.parse("url =")


def test_rejects_unknown_site_key():
	with assert_raises(ConfigError):
		Config.parse('title = "Liam Egan"')


def test_rejects_unknown_assets_key():
	with assert_raises(ConfigError):
		Config.parse('[assets]\nfonts = ["inter"]')


def test_rejects_unknown_route_key():
	with assert_raises(ConfigError):
		Config.parse('[[routes]]\npath = "/"\nview = "home"\nlayout = "base"')


def test_rejects_unknown_collection_key():
	with assert_raises(ConfigError):
		Config.parse('[collections.articles]\nsort = "date"\ntitle = "Articles"')


def test_rejects_route_without_path():
	with assert_raises(ConfigError):
		Config.parse('[[routes]]\nview = "home"')


def test_rejects_route_without_view():
	with assert_raises(ConfigError):
		Config.parse('[[routes]]\npath = "/"')


def test_rejects_duplicate_route_names():
	with assert_raises(ConfigError):
		Config.parse(
			'[[routes]]\nname = "home"\npath = "/"\nview = "home"\n'
			'[[routes]]\nname = "home"\npath = "/home"\nview = "home"'
		)


def test_rejects_route_with_item_and_collection():
	with assert_raises(ConfigError):
		Config.parse(
			'[[routes]]\npath = "/articles/{name}"\nview = "articles/show"\n'
			'item = "about"\ncollection = "articles"'
		)


def test_rejects_placeholder_other_than_name():
	with assert_raises(ConfigError):
		Config.parse(
			'[[routes]]\npath = "/articles/{id}"\nview = "articles/show"\n'
			'collection = "articles"'
		)


def test_rejects_name_placeholder_with_converter():
	with assert_raises(ConfigError):
		Config.parse(
			'[[routes]]\npath = "/articles/{name:uuid}"\nview = "articles/show"\n'
			'collection = "articles"'
		)


def test_rejects_per_item_route_without_name_placeholder():
	with assert_raises(ConfigError):
		Config.parse(
			'[[routes]]\npath = "/articles"\nview = "articles/show"\ncollection = "articles"'
		)


def test_rejects_per_item_route_ending_in_slash():
	with assert_raises(ConfigError):
		Config.parse(
			'[[routes]]\npath = "/articles/{name}/"\nview = "articles/show"\n'
			'collection = "articles"'
		)


def test_rejects_single_path_with_name_placeholder():
	with assert_raises(ConfigError):
		Config.parse('[[routes]]\npath = "/articles/{name}"\nview = "articles/show"')


def test_rejects_collection_without_sort():
	with assert_raises(ConfigError):
		Config.parse('[collections.articles]\norder = "desc"')


def test_rejects_unknown_collection_order():
	with assert_raises(ConfigError):
		Config.parse('[collections.articles]\nsort = "date"\norder = "sideways"')


def test_rejects_value_of_wrong_type():
	with assert_raises(ConfigError):
		Config.parse('[[routes]]\npath = 5\nview = "home"')


def test_rejects_invalid_base_url():
	with assert_raises(ConfigError):
		Config.parse('url = "https://"')


def test_rejects_invalid_item_path():
	with assert_raises(ConfigError):
		Config.parse('[[routes]]\npath = "/about"\nview = "page"\nitem = "/about"')


def test_rejects_invalid_collection_name():
	with assert_raises(ConfigError):
		Config.parse('[collections."articles/"]\nsort = "date"')
