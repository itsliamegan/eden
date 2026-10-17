from helios.view import Engine, file, memory
from luna.test.assertion import assert_eq
from markupsafe import Markup

from eden.markdown import Link, VIEWS_DIR


def test_renders_link():
	engine = Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)])

	html = engine.render(
		Link(href="/writing/tranquility", title=None, content=Markup("Tranquility"))
	)

	assert_eq(html, '<a href="/writing/tranquility">Tranquility</a>')


def test_renders_link_with_title():
	engine = Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)])

	html = engine.render(
		Link(
			href="/writing/tranquility",
			title="On quiet",
			content=Markup("Tranquility"),
		)
	)

	assert_eq(
		html,
		'<a href="/writing/tranquility" title="On quiet">Tranquility</a>',
	)
