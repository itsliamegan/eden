from pathlib import Path
from ..filesystem import read_site, write_site

def build():
	root_dir = Path.cwd()
	public_dir = root_dir.joinpath("public")

	site = read_site(root_dir)
	write_site(public_dir, site.build())
