from os import chdir as set_working_dir
from pathlib import Path
from tempfile import TemporaryDirectory

from luna.test.assertion import assert_eq, assert_not, assert_raises

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

		assert_eq(contents, "<h1>About</h1>")


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

		assert_eq(contents, "<h1>Home</h1>")


def test_builds_page_with_separator_in_body():
	with TemporaryDirectory() as tempdir:
		set_working_dir(tempdir)
		create("blog", minimal=True)

		root_dir = Path(tempdir).joinpath("blog")
		src_dir = root_dir.joinpath("src")
		content_dir = src_dir.joinpath("content")

		about_page_file = content_dir.joinpath("about.md")
		about_page_file.write_text('title = "About"\n---\nFirst\n\n---\nSecond\n')

		set_working_dir(root_dir)
		build()

		public_dir = root_dir.joinpath("public")
		about_document_file = public_dir.joinpath("about.html")
		contents = about_document_file.read_text()

		assert_eq(contents, "<p>First</p>\n<hr />\n<p>Second</p>\n")


def test_builds_collection_index_page():
	with TemporaryDirectory() as tempdir:
		set_working_dir(tempdir)
		create("blog", minimal=True)

		root_dir = Path(tempdir).joinpath("blog")
		src_dir = root_dir.joinpath("src")
		content_dir = src_dir.joinpath("content")
		articles_dir = content_dir.joinpath("articles")
		articles_dir.mkdir()

		articles_page_file = content_dir.joinpath("articles.html")
		articles_page_file.write_text("<h1>Articles</h1>")
		article_page_file = articles_dir.joinpath("hello_world.html")
		article_page_file.write_text("<h1>Hello, World</h1>")

		set_working_dir(root_dir)
		build()

		public_dir = root_dir.joinpath("public")
		articles_document_file = public_dir.joinpath("articles", "index.html")
		article_document_file = public_dir.joinpath("articles", "hello-world.html")

		assert_eq(articles_document_file.read_text(), "<h1>Articles</h1>")
		assert_eq(article_document_file.read_text(), "<h1>Hello, World</h1>")
		assert_not(public_dir.joinpath("articles.html").exists())


def test_rejects_index_page_in_collection():
	with TemporaryDirectory() as tempdir:
		set_working_dir(tempdir)
		create("blog", minimal=True)

		root_dir = Path(tempdir).joinpath("blog")
		src_dir = root_dir.joinpath("src")
		content_dir = src_dir.joinpath("content")
		articles_dir = content_dir.joinpath("articles")
		articles_dir.mkdir()

		index_page_file = articles_dir.joinpath("index.html")
		index_page_file.write_text("<h1>Articles</h1>")

		set_working_dir(root_dir)

		with assert_raises(ValueError):
			build()
