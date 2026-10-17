from dataclasses import dataclass
import tomllib
from typing import Any, Literal, NotRequired, Self, TypedDict

from cattrs import Converter, transform_error
from cattrs.errors import BaseValidationError
from cattrs.v import format_exception
from helios.url import Pattern, URL
from helios.url.convert import Str

from .content import ContentPath, Order
from .routing import Route
from .routing.route import PerItemExpansion, SingleExpansion

DEFAULT_BASE_URL = URL.parse("http://localhost:3000")

# cattrs makes a str from any value by default, so the str hook rejects values
# of other types. The other hooks build eden's types from text.
CONVERTER = Converter(forbid_extra_keys=True)
CONVERTER.register_structure_hook(str, lambda value, _: require_string(value))
CONVERTER.register_structure_hook(
	URL,
	lambda value, _: URL.parse(require_string(value)),
)
CONVERTER.register_structure_hook(
	ContentPath,
	lambda value, _: ContentPath.parse(require_string(value)),
)


@dataclass
class Config:
	"""A site's parsed config, which holds how the site is built."""

	base_url: URL
	scripts: list[str]
	styles: list[str]
	routes: list[Route]
	orders: dict[ContentPath, Order]

	@classmethod
	def parse(cls, text: str) -> Self:
		try:
			table = CONVERTER.structure(tomllib.loads(text), SiteTable)
		except tomllib.TOMLDecodeError as error:
			raise ConfigError(f"invalid TOML: {error}") from error
		except BaseValidationError as error:
			descriptions = transform_error(
				error,
				path="config",
				format_exception=describe,
			)
			raise ConfigError(", ".join(descriptions)) from error

		base_url = table.get("url", DEFAULT_BASE_URL)
		if base_url.host is None:
			raise ConfigError(f"url is not absolute: {base_url}")

		routes = []
		names = set()
		for route_table in table.get("routes", []):
			route = Config.route(route_table)
			if route.name in names:
				raise ConfigError(f"duplicate route name: {route.name}")
			if route.name is not None:
				names.add(route.name)
			routes.append(route)

		orders = {}
		for collection, collection_table in table.get("collections", {}).items():
			orders[collection] = Order(
				collection_table["sort"],
				collection_table.get("order", "asc"),
			)

		assets = table.get("assets", AssetsTable())
		return cls(
			base_url,
			assets.get("scripts", []),
			assets.get("styles", []),
			routes,
			orders,
		)

	@staticmethod
	def route(table: RouteTable) -> Route:
		if "item" in table and "collection" in table:
			raise ConfigError(
				f"route declares both an item and a collection: {table["path"]}"
			)

		try:
			path = Pattern.parse(table["path"])
		except ValueError as error:
			raise ConfigError(f"invalid route path: {table["path"]}") from error
		for parameter in path.parameters.values():
			# Only accept a single "name" parameter that uses the "str" converter.
			if parameter.name != "name" or not isinstance(parameter.converter, Str):
				raise ConfigError(f"placeholder other than {{name}}: {table["path"]}")

		if "collection" in table:
			if "name" not in path.parameters:
				raise ConfigError(f"per-item route without {{name}}: {table["path"]}")
			if path.trailing_slash:
				raise ConfigError(f"per-item route ends in a slash: {table["path"]}")
			expansion = PerItemExpansion(table["collection"])
		else:
			if path.parameters:
				raise ConfigError(f"single route with {{name}}: {table["path"]}")
			expansion = SingleExpansion(table.get("item"))

		return Route(table.get("name"), path, table["view"], expansion)


class SiteTable(TypedDict):
	url: NotRequired[URL]
	assets: NotRequired[AssetsTable]
	routes: NotRequired[list[RouteTable]]
	collections: NotRequired[dict[ContentPath, CollectionTable]]


class AssetsTable(TypedDict):
	scripts: NotRequired[list[str]]
	styles: NotRequired[list[str]]


class RouteTable(TypedDict):
	path: str
	view: str
	name: NotRequired[str]
	item: NotRequired[ContentPath]
	collection: NotRequired[ContentPath]


class CollectionTable(TypedDict):
	sort: str
	order: NotRequired[Literal["asc", "desc"]]


def require_string(value: Any) -> str:
	if not isinstance(value, str):
		raise TypeError(f"got {value!r}")

	return value


def describe(exception: BaseException, target: type | None) -> str:
	description = format_exception(exception, target)
	# The hooks raise these with a message that says what is wrong with the
	# value, which cattrs' description leaves out.
	if isinstance(exception, (ValueError, TypeError)):
		return f"{description} ({exception})"
	else:
		return description


class ConfigError(Exception):
	pass
