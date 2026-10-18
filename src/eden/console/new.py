from pathlib import Path
import shutil

from luna.cli import Command, argument

SKELETON_DIR = Path(Path(__file__).parent.parent, "skeleton")


class New(Command):
	"""Create a new site."""

	name = "new"
	directory: Path = argument(help="where to create the site")

	def run(self):
		try:
			shutil.copytree(
				SKELETON_DIR,
				self.directory,
				ignore=shutil.ignore_patterns(".gitkeep"),
			)
		except FileExistsError:
			self.fail(f"directory already exists: {self.directory}")

		self.logger.info(f"created site in {self.directory}")
