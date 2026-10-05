from pathlib import Path

from luna.cli import Command

from ..filesystem import read_site, write_documents


class Build(Command):
	"""Build an existing site."""

	name = "build"

	def run(self):
		root_dir = Path.cwd()
		public_dir = root_dir.joinpath("public")

		site = read_site(root_dir)
		write_documents(public_dir, site.build())
