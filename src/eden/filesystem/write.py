from pathlib import Path
from shutil import rmtree

from ..artifact import Document, Site


def write_site(public_dir: Path, site: Site):
	if public_dir.exists():
		rmtree(public_dir)
	else:
		public_dir.mkdir()

	for document in site.documents:
		write_document(public_dir, document)


def write_document(public_dir: Path, document: Document):
	file = public_dir.joinpath(*document.permalink.components)
	if document.permalink.is_index:
		file = file.joinpath("index.html")
	else:
		file = file.with_suffix(".html")

	file.parent.mkdir(parents=True, exist_ok=True)
	file.write_text(document.contents)
