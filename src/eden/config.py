from dataclasses import dataclass
import tomllib
from typing import Any, Self

from helios.url import Pattern, URL
from helios.url.convert import Str

from .content import Order
from .routing import PerItemExpansion, Route, SingleExpansion

SITE_KEYS = {"url", "assets", "routes", "collections"}
ASSETS_KEYS = {"scripts", "styles"}
ROUTE_KEYS = {"name", "path", "view", "item", "collection"}
COLLECTION_KEYS = {"sort", "order"}


@dataclass
class Config:
	"""A site's parsed `site.toml`, which holds how the site is built."""

	base_url: URL
	scripts: list[str]
	styles: list[str]
	routes: list[Route]
	orders: dict[str, Order]

	@classmethod
	def parse(cls, text: str) -> Self:
		try:
			table = tomllib.loads(text)
		except tomllib.TOMLDecodeError as error:
			raise ConfigError(f"invalid TOML: {error}") from error
		Config.reject_unknown_keys(table, SITE_KEYS, "site")
		assets = table.get("assets", {})
		Config.reject_unknown_keys(assets, ASSETS_KEYS, "assets")

		routes = []
		names = set()
		for route_table in table.get("routes", []):
			route = Config.parse_route(route_table)
			if route.name in names:
				raise ConfigError(f"duplicate route name: {route.name}")
			if route.name is not None:
				names.add(route.name)
			routes.append(route)

		orders = {}
		for name, collection_table in table.get("collections", {}).items():
			orders[name] = Config.parse_order(name, collection_table)

		return cls(
			Config.parse_url(table.get("url", "http://localhost:3000")),
			assets.get("scripts", []),
			assets.get("styles", []),
			routes,
			orders,
		)

	@staticmethod
	def parse_url(text: str) -> URL:
		try:
			url = URL.parse(text)
		except ValueError as error:
			raise ConfigError(f"invalid url: {text}") from error

		if url.host is None:
			raise ConfigError(f"url is not absolute: {text}")
		return url

	@staticmethod
	def parse_route(table: dict[str, Any]) -> Route:
		Config.reject_unknown_keys(table, ROUTE_KEYS, "route")
		for key in ("path", "view"):
			if key not in table:
				raise ConfigError(f"missing key in route: {key}")
		if "item" in table and "collection" in table:
			raise ConfigError(f"route has an item and a collection: {table["path"]}")

		try:
			path = Pattern.parse(table["path"])
		except ValueError as error:
			raise ConfigError(f"invalid route path: {table["path"]}") from error
		for parameter in path.parameters.values():
			# Pattern accepts any name and converter, but an item's name is the
			# only value a route can fill in.
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

	@staticmethod
	def parse_order(name: str, table: dict[str, Any]) -> Order:
		Config.reject_unknown_keys(table, COLLECTION_KEYS, f"collection {name}")
		if "sort" not in table:
			raise ConfigError(f"missing key in collection {name}: sort")

		match table.get("order", "asc"):
			case "asc":
				return Order(table["sort"], "asc")
			case "desc":
				return Order(table["sort"], "desc")
			case direction:
				raise ConfigError(f"unknown order in collection {name}: {direction}")

	@staticmethod
	def reject_unknown_keys(table: dict[str, Any], keys: set[str], where: str):
		for key in table:
			if key not in keys:
				raise ConfigError(f"unknown key in {where}: {key}")


class ConfigError(Exception):
	pass
