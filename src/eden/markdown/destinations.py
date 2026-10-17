from collections.abc import Mapping
import html
from urllib.parse import SplitResult, quote, urlsplit

from ..content import ContentPath, Item
from ..routing import RouteNotFoundError, URLs
from .error import MarkdownError

SAFE_CHARACTERS = "/#:()*?=%@+,&"


class Destinations:
	"""The URLs that the destinations of links and images in items' Markdown stand for.

	A destination with a scheme or a host passes through, and so does any other
	relative reference but a link to a Markdown file, which names an item.
	"""

	def __init__(self, urls: URLs, items: Mapping[ContentPath, Item]):
		self.urls = urls
		self.items = items

	def link(self, destination: str, item: Item) -> str:
		text = html.unescape(destination)
		reference = urlsplit(text)
		if reference.scheme or reference.netloc:
			url = text
		elif reference.path.startswith("/"):
			url = self.path_url(reference)
		elif reference.path.endswith(".md"):
			url = self.item_url(reference, item)
		else:
			url = text
		return quote(url, safe=SAFE_CHARACTERS)

	def image(self, destination: str) -> str:
		text = html.unescape(destination)
		reference = urlsplit(text)
		if reference.scheme or reference.netloc:
			url = text
		elif reference.path.startswith("/"):
			url = self.path_url(reference)
		else:
			url = text
		return quote(url, safe=SAFE_CHARACTERS)

	def path_url(self, reference: SplitResult) -> str:
		path = self.urls.path(reference.path).path
		return reference._replace(path=path).geturl()

	def item_url(self, reference: SplitResult, item: Item) -> str:
		target_path = item.path.resolve(reference.path.removesuffix(".md"))
		target = self.items.get(target_path)
		if target is None:
			raise MarkdownError(
				f"link target is not an item: {target_path} in {item.path}"
			)

		try:
			path = self.urls.item(target).path
		except RouteNotFoundError as error:
			raise MarkdownError(
				f"link target has no page: {target_path} in {item.path}"
			) from error
		return reference._replace(path=path).geturl()
