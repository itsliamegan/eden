from cmarkgfm import github_flavored_markdown_to_html as gfm_to_html

from . import html
from .format import Format


class Format(Format):
	def compile(self, source: str) -> html.Compiled:
		return html.Compiled(gfm_to_html(source))
