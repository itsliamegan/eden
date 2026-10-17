from dataclasses import dataclass

from helios.url import Pattern

from ..content import ContentPath


@dataclass
class Route:
	"""A path that renders a view. Includes how it expands into pages.

	The expansion names content as the site config writes it and is resolved
	against the site's content when the route is expanded into pages.
	"""

	name: str | None
	path: Pattern
	view: str
	expansion: SingleExpansion | PerItemExpansion


@dataclass
class SingleExpansion:
	"""An expansion of a route into a page with a single item or no item."""

	item: ContentPath | None


@dataclass
class PerItemExpansion:
	"""An expansion of a route into a page for every item in a collection."""

	collection: ContentPath
