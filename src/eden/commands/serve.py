from dataclasses import dataclass
from pathlib import Path
import sys
from threading import Thread

from helios.url import URL
from luna.cli import Command, argument
from watchfiles import Change, DefaultFilter, watch
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.serving import make_server
from werkzeug.utils import send_from_directory
from werkzeug.wrappers import Request, Response

from ..config import Config, ConfigError
from ..driver import file
from ..site import Site
from .build import ANTICIPATED_ERRORS

HOST = "localhost"
PORT = 3000
ADDRESS = URL("", scheme="http", host=HOST, port=PORT)


class Serve(Command):
	"""Serve a site for local work, rebuilding it when its source changes."""

	name = "serve"
	directory: Path = argument(default=Path("."), help="the site's directory")

	def run(self):
		driver = file.Driver(self.directory)
		application = Application(driver.public)
		# Werkzeug reports a failure to bind and exits.
		server = make_server(HOST, PORT, application, threaded=True)
		Thread(target=server.serve_forever, daemon=True).start()

		try:
			self.rebuild(driver, application)
			for _ in watch(
				self.directory,
				watch_filter=Filter(self.directory, driver),
			):
				self.rebuild(driver, application)
		except KeyboardInterrupt:
			pass
		finally:
			server.shutdown()
			server.server_close()

	def rebuild(self, driver: file.Driver, application: Application):
		path = Path(self.directory, "site.toml")
		try:
			text = path.read_text()
		except FileNotFoundError:
			print(
				f"eden: error: invalid site config: file not found: {path}",
				file=sys.stderr,
			)
			return

		try:
			parsed = Config.parse(text)
			base_url = URL(
				parsed.base_url.path,
				scheme=ADDRESS.scheme,
				host=ADDRESS.host,
				port=ADDRESS.port,
			)
			config = Config(
				base_url,
				parsed.scripts,
				parsed.styles,
				parsed.routes,
				parsed.orders,
			)
			application.base_path = base_url.path

			driver.empty()
			manifest = driver.compile(
				config.scripts,
				config.styles,
				minify=False,
				sourcemap=True,
			)
			site = Site.read(config, manifest, driver)
			driver.write(site.build())
			driver.copy()
		except ConfigError as error:
			print(f"eden: error: invalid site config: {error}", file=sys.stderr)
		except ANTICIPATED_ERRORS as error:
			print(f"eden: error: {error}", file=sys.stderr)


@dataclass
class Application:
	"""A WSGI application that serves a site's public directory as a static host.

	It serves the directory under the base path, so a request outside the base
	path is not found. A request path finds the file at that path, the index
	file of a path ending in a slash, or the HTML file of that name.
	"""

	public: Path
	base_path: str = ""

	def __call__(self, environ, start_response):
		request = Request(environ)
		try:
			response = self.respond(request)
		except HTTPException as error:
			response = error
		return response(environ, start_response)

	def respond(self, request: Request) -> Response:
		prefix = self.base_path.rstrip("/")
		if request.path != prefix and not request.path.startswith(f"{prefix}/"):
			raise NotFound()

		path = request.path[len(prefix) :].lstrip("/")
		if path == "" or path.endswith("/"):
			return send_from_directory(
				self.public, f"{path}index.html", request.environ
			)
		else:
			try:
				return send_from_directory(self.public, path, request.environ)
			except NotFound:
				return send_from_directory(
					self.public,
					f"{path}.html",
					request.environ,
				)


class Filter(DefaultFilter):
	"""Passes the site's config and every file under its source directory."""

	def __init__(self, directory: Path, driver: file.Driver):
		super().__init__()
		self.config = Path(directory, "site.toml").resolve()
		self.source = driver.source.resolve()

	def __call__(self, change: Change, path: str) -> bool:
		if not super().__call__(change, path):
			return False

		changed = Path(path).resolve()
		return changed == self.config or changed.is_relative_to(self.source)
