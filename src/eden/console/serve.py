from dataclasses import dataclass
from pathlib import Path
import socket
from threading import Thread
import time

from helios.url import URL
from luna import inflect
from luna.cli import Command, argument
from luna.logger import Logger
from watchfiles import Change, DefaultFilter, watch
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.serving import WSGIRequestHandler, make_server
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
	directory: Path = argument(default=Path("."), help="the site's root directory")

	def run(self):
		# Try to bind to the address directly in order to support a custom error
		# message instead of letting Werkzeug print its own.
		try:
			listener = socket.create_server((HOST, PORT))
		except OSError as error:
			self.fail(f"could not listen on port {PORT}: {error.strerror}")

		try:
			driver = file.Driver(self.directory)
			application = Application(driver.public, self.logger)
			server = make_server(
				HOST,
				PORT,
				application,
				threaded=True,
				request_handler=RequestHandler,
				fd=listener.fileno(),
			)
		finally:
			# The Werkzeug server holds its own duplicate of the socket.
			listener.close()

		Thread(target=server.serve_forever, daemon=True).start()

		try:
			self.rebuild(driver, application)
			# The base path is known only once the config parses.
			address = URL(
				application.base_path,
				scheme=ADDRESS.scheme,
				host=ADDRESS.host,
				port=ADDRESS.port,
			)
			self.logger.info(f"serving at {address}")

			directory = self.directory.resolve()
			for changes in watch(
				self.directory,
				watch_filter=Filter(self.directory, driver),
			):
				for change, path in sorted(changes):
					relative = Path(path).resolve().relative_to(directory)
					match change:
						case Change.added:
							self.logger.info(f"added {relative}")
						case Change.modified:
							self.logger.info(f"changed {relative}")
						case Change.deleted:
							self.logger.info(f"deleted {relative}")
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
			self.logger.error(f"invalid site config: file not found: {path}")
			return

		start = time.perf_counter()
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
			documents = site.build()
			driver.write(documents)
			driver.copy()
		except ConfigError as error:
			self.logger.error(f"invalid site config: {error}")
		except ANTICIPATED_ERRORS as error:
			self.logger.error(str(error))
		else:
			seconds = time.perf_counter() - start
			pages = inflect.count(len(documents), "page")
			self.logger.info(f"built {pages} in {seconds:.2f}s")


@dataclass
class Application:
	"""A WSGI application that serves a site's public directory as a static host.

	It serves the directory under the base path, so a request outside the base
	path is not found. A request path finds the file at that path, the index
	file of a path ending in a slash, or the HTML file of that name.
	"""

	public: Path
	logger: Logger
	base_path: str = ""

	def __call__(self, environ, start_response):
		request = Request(environ)
		try:
			response = self.respond(request)
		except NotFound as error:
			self.logger.warn(f"not found: {request.path}")
			response = error
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


class RequestHandler(WSGIRequestHandler):
	"""Handles a request without logging it, because the application reports the requests that fail."""

	def log_request(self, code: int | str = "-", size: int | str = "-"):
		pass


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
