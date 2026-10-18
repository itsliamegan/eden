from pathlib import Path
import shutil

from helios.assets import Bundler, Manifest
from helios.view import file

from ..content import Collection, ContentError, ContentPath, Item, Items
from ..document import Document
from .driver import Driver
from .error import DuplicateFileError


class Driver(Driver):
	"""The resources of a site accessed on disk."""

	def __init__(self, root: Path):
		self.root = root
		self.content = Path(root, "src", "content")
		self.assets = Path(root, "src", "assets")
		self.static = Path(root, "src", "static")
		self.public = Path(root, "public")

	def items(self) -> list[Item]:
		if not self.content.is_dir():
			return []

		items = []
		for item in self.read(self.content):
			if not Path(self.content, item.name).is_dir():
				items.append(item)
		return items

	def collections(self) -> list[Collection]:
		collections = []
		indexes: dict[ContentPath, Item] = {}
		for directory, names, _ in self.content.walk():
			for name in list(names):
				if name.startswith("."):
					names.remove(name)
			names.sort()

			items = []
			for item in self.read(directory):
				if item.name in names:
					indexes[item.path] = item
				else:
					items.append(item)

			if directory != self.content:
				path = ContentPath(directory.relative_to(self.content).parts)
				collections.append(Collection(path, Items(items), indexes.get(path)))
		return collections

	def views(self) -> file.Driver:
		return file.Driver(Path(self.root, "src", "views"))

	def read(self, directory: Path) -> list[Item]:
		"""Read the items of a directory's files, ignoring hidden files, in name order."""
		sources = []
		for source in directory.iterdir():
			if source.is_file() and not source.name.startswith("."):
				sources.append(source)
		sources.sort(key=lambda source: source.stem)

		items = []
		names = set()
		for source in sources:
			if source.suffix not in (".md", ".toml"):
				raise ContentError(f"unknown content file: {source}")
			if source.stem == "index":
				raise ContentError(f"item named index: {source}")
			if source.stem in names:
				raise ContentError(f"duplicate item: {source}")
			names.add(source.stem)

			path = ContentPath(
				(*directory.relative_to(self.content).parts, source.stem)
			)
			if source.suffix == ".md":
				items.append(Item.markdown(path, source.read_text()))
			else:
				items.append(Item.toml(path, source.read_text()))
		return items

	def write(self, documents: list[Document]):
		for document in documents:
			relative = document.path.lstrip("/")
			if document.path.endswith("/"):
				target = Path(self.public, relative, "index.html")
			elif "." in Path(relative).name:
				target = Path(self.public, relative)
			else:
				target = Path(self.public, f"{relative}.html")

			if target.exists():
				raise DuplicateFileError(f"duplicate file: {target}")

			target.parent.mkdir(parents=True, exist_ok=True)
			target.write_text(document.text)

	def compile(
		self,
		scripts: list[str],
		styles: list[str],
		*,
		minify: bool,
		sourcemap: bool,
	) -> Manifest:
		compiled = Bundler(self.root).compile(
			self.assets,
			Path(self.public, "assets"),
			scripts,
			styles,
			minify=minify,
			sourcemap=sourcemap,
		)
		return compiled.manifest

	def copy(self):
		"""Copy the static files from the source directory to the public directory."""
		for source in sorted(self.static.rglob("*")):
			if not source.is_file():
				continue

			target = Path(self.public, source.relative_to(self.static))
			if target.exists():
				raise DuplicateFileError(f"duplicate file: {target}")

			target.parent.mkdir(parents=True, exist_ok=True)
			shutil.copy2(source, target)

	def empty(self):
		self.public.mkdir(parents=True, exist_ok=True)
		for child in self.public.iterdir():
			if child.is_dir() and not child.is_symlink():
				shutil.rmtree(child)
			else:
				child.unlink()
