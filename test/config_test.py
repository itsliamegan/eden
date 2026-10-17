from helios.url import Pattern
from luna.test.assertion import assert_eq, assert_raises

from eden.config import Config, ConfigError
from eden.content import Order
from eden.routing import PerItemExpansion, Route, SingleExpansion


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
		'[[routes]]\nname = "essay"\npath = "/writing/{name}.xml"\n'
		'view = "writing/show"\ncollection = "writing"'
	)

	assert_eq(
		config.routes,
		[
			Route(
				"essay",
				Pattern.parse("/writing/{name}.xml"),
				"writing/show",
				PerItemExpansion("writing"),
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
				SingleExpansion("guides/database"),
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

	assert_eq(config.orders, {"guides/database": Order("date", "desc")})


def test_defaults_collection_order_to_ascending():
	config = Config.parse('[collections.writing]\nsort = "position"')

	assert_eq(config.orders, {"writing": Order("position", "asc")})


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
		Config.parse('[collections.writing]\nsort = "date"\ntitle = "Writing"')


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
			'[[routes]]\npath = "/writing/{name}"\nview = "writing/show"\n'
			'item = "about"\ncollection = "writing"'
		)


def test_rejects_placeholder_other_than_name():
	with assert_raises(ConfigError):
		Config.parse(
			'[[routes]]\npath = "/writing/{id}"\nview = "writing/show"\n'
			'collection = "writing"'
		)


def test_rejects_name_placeholder_with_converter():
	with assert_raises(ConfigError):
		Config.parse(
			'[[routes]]\npath = "/writing/{name:uuid}"\nview = "writing/show"\n'
			'collection = "writing"'
		)


def test_rejects_per_item_route_without_name_placeholder():
	with assert_raises(ConfigError):
		Config.parse(
			'[[routes]]\npath = "/writing"\nview = "writing/show"\ncollection = "writing"'
		)


def test_rejects_per_item_route_ending_in_slash():
	with assert_raises(ConfigError):
		Config.parse(
			'[[routes]]\npath = "/writing/{name}/"\nview = "writing/show"\n'
			'collection = "writing"'
		)


def test_rejects_single_path_with_name_placeholder():
	with assert_raises(ConfigError):
		Config.parse('[[routes]]\npath = "/writing/{name}"\nview = "writing/show"')


def test_rejects_collection_without_sort():
	with assert_raises(ConfigError):
		Config.parse('[collections.writing]\norder = "desc"')


def test_rejects_unknown_collection_order():
	with assert_raises(ConfigError):
		Config.parse('[collections.writing]\nsort = "date"\norder = "sideways"')
