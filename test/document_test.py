from pathlib import Path

from luna.test.assertion import assert_eq

from eden.document import Document
from eden.permalink import Permalink


def test_places_root_at_index_file():
	document = Document(Permalink.root(), contents="")

	assert_eq(document.path, Path("index.html"))


def test_places_index_at_index_file_in_directory():
	document = Document(Permalink(["articles"], is_index=True), contents="")

	assert_eq(document.path, Path("articles/index.html"))


def test_places_entry_at_html_file():
	document = Document(Permalink(["articles", "hello-world"]), contents="")

	assert_eq(document.path, Path("articles/hello-world.html"))


def test_keeps_dots_in_entry_name():
	document = Document(Permalink(["v1.2"]), contents="")

	assert_eq(document.path, Path("v1.2.html"))
