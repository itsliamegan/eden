from os import chdir as set_working_dir
from pathlib import Path
from tempfile import TemporaryDirectory

from eden.commands import build, create


def test_builds_single_page():
	with TemporaryDirectory() as tempdir:
		set_working_dir(tempdir)
		create("blog", minimal=True)

		root_dir = Path(tempdir).joinpath("blog")
		src_dir = root_dir.joinpath("src")
		content_dir = src_dir.joinpath("content")

		about_page_file = content_dir.joinpath("about.html")
		about_page_file.write_text("<h1>About</h1>")

		set_working_dir(root_dir)
		build()

		public_dir = root_dir.joinpath("public")
		about_document_file = public_dir.joinpath("about.html")
		contents = about_document_file.read_text()

		assert contents == "<h1>About</h1>"


def test_builds_single_index_page():
	with TemporaryDirectory() as tempdir:
		set_working_dir(tempdir)
		create("blog", minimal=True)

		root_dir = Path(tempdir).joinpath("blog")
		src_dir = root_dir.joinpath("src")
		content_dir = src_dir.joinpath("content")

		index_page_file = content_dir.joinpath("index.html")
		index_page_file.write_text("<h1>Home</h1>")

		set_working_dir(root_dir)
		build()

		public_dir = root_dir.joinpath("public")
		about_document_file = public_dir.joinpath("index.html")
		contents = about_document_file.read_text()

		assert contents == "<h1>Home</h1>"
