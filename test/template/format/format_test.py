from pathlib import Path

from luna.test.assertion import assert_is_instance, assert_raises

from eden.template.format import Format, handlebars, html, markdown


def test_finds_format_for_file():
	assert_is_instance(Format.for_file(Path("about.html")), html.Format)
	assert_is_instance(Format.for_file(Path("about.md")), markdown.Format)
	assert_is_instance(Format.for_file(Path("about.hbs")), handlebars.Format)


def test_rejects_unknown_suffix():
	with assert_raises(ValueError):
		Format.for_file(Path("about.exe"))
