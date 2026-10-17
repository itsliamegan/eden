from dataclasses import dataclass

from ..content import Item
from .route import Route


@dataclass
class Page:
	"""A path the build renders. Includes its route and the item its view is handed."""

	path: str
	route: Route
	item: Item | None
