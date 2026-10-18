from pathlib import Path

from helios.assets import BundlerNotFoundError, CompileError, EntryNotFoundError
from helios.view import ComponentError
from jinja2 import TemplateError
from luna.cli import Command, argument

from ..config import Config, ConfigError
from ..content import ContentError, ContentNotFoundError
from ..driver import DuplicateFileError, file
from ..markdown import MarkdownError
from ..routing import RouteError, RouteNotFoundError
from ..site import DuplicateDocumentError, Site, ViewNotFoundError

# The failures of a site that a command reports instead of crashing on.
ANTICIPATED_ERRORS = (
	ContentError,
	ContentNotFoundError,
	RouteError,
	RouteNotFoundError,
	MarkdownError,
	ViewNotFoundError,
	DuplicateDocumentError,
	DuplicateFileError,
	BundlerNotFoundError,
	CompileError,
	EntryNotFoundError,
	ComponentError,
	TemplateError,
)


class Build(Command):
	"""Build a site for a deploy."""

	name = "build"
	directory: Path = argument(default=Path("."), help="the site's directory")

	def run(self):
		path = Path(self.directory, "site.toml")
		try:
			text = path.read_text()
		except FileNotFoundError:
			self.fail(f"invalid site config: file not found: {path}")

		try:
			config = Config.parse(text)

			driver = file.Driver(self.directory)
			driver.empty()
			manifest = driver.compile(
				config.scripts,
				config.styles,
				minify=True,
				sourcemap=False,
			)
			site = Site.read(config, manifest, driver)
			driver.write(site.build())
			driver.copy()
		except ConfigError as error:
			self.fail(f"invalid site config: {error}")
		except ANTICIPATED_ERRORS as error:
			self.fail(str(error))
