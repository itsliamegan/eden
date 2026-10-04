from pathlib import Path

from pytest import raises

from eden.template.format import Format, handlebars, html, markdown


def test_finds_format_for_file():
	assert isinstance(Format.for_file(Path("about.html")), html.Format)
	assert isinstance(Format.for_file(Path("about.md")), markdown.Format)
	assert isinstance(Format.for_file(Path("about.hbs")), handlebars.Format)


def test_rejects_unknown_suffix():
	with raises(ValueError):
		Format.for_file(Path("about.exe"))
