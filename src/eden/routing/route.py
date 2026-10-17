from dataclasses import dataclass

from helios.url import Pattern


@dataclass
class Route:
	"""A path that renders a view. Includes how it expands into pages.

	The expansion names content as `site.toml` writes it, and is resolved
	against the site's content when the route is expanded into pages.
	"""

	name: str | None
	path: Pattern
	view: str
	expansion: SingleExpansion | PerItemExpansion


@dataclass
class SingleExpansion:
	"""One page, for an item by its path in the content, or for no item."""

	item: str | None


@dataclass
class PerItemExpansion:
	"""One page for each item in a collection, by the collection's name."""

	collection: str
