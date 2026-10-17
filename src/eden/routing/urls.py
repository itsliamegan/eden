from collections.abc import Sequence
from pathlib import PurePosixPath

from helios.url import Pattern, URL

from ..content import Item
from .error import RouteError, RouteNotFoundError
from .route import PerItemExpansion, Route


class URLs:
	"""A builder of URLs for routes and paths under a base URL.

	The base URL's path prefixes every URL, because the host serves the site
	there.
	"""

	def __init__(self, routes: Sequence[Route], base_url: URL):
		if base_url.scheme is None or base_url.host is None:
			raise ValueError("base URL must be absolute")

		self.routes = {}
		for route in routes:
			if route.name is not None:
				self.routes[route.name] = route
		self.base_url = base_url
		self.prefix = Pattern.parse(base_url.path)

	def route(self, name: str, item: Item | None = None, absolute: bool = False) -> URL:
		route = self.routes.get(name)
		if route is None:
			raise RouteNotFoundError(f"route not found: {name}")

		if isinstance(route.expansion, PerItemExpansion):
			if item is None:
				raise RouteError(f"route needs an item: {name}")
			collection = PurePosixPath(route.expansion.collection)
			if PurePosixPath(item.path).parent != collection:
				raise RouteError(f"item not in route's collection: {item.path}")
			path = route.path.path({"name": item.name})
		else:
			if item is not None:
				raise RouteError(f"route takes no item: {name}")
			path = route.path.path()
		return self.path(path, absolute)

	def path(self, path: str, absolute: bool = False) -> URL:
		path = Pattern.parse(path).prefixed(self.prefix).path()
		if absolute:
			return URL(
				path,
				scheme=self.base_url.scheme,
				host=self.base_url.host,
				port=self.base_url.port,
			)
		else:
			return URL(path)
