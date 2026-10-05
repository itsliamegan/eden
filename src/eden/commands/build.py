from pathlib import Path

from ..filesystem import read_site, write_documents


def build():
	root_dir = Path.cwd()
	public_dir = root_dir.joinpath("public")

	site = read_site(root_dir)
	write_documents(public_dir, site.build())
