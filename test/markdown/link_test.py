from helios.view import Engine, file, memory
from luna.test.assertion import assert_eq
from markupsafe import Markup

from eden.markdown import Link, VIEWS_DIR


def test_renders_link():
	engine = Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)])

	html = engine.render(
		Link(href="/articles/intro", title=None, content=Markup("Intro"))
	)

	assert_eq(html, '<a href="/articles/intro">Intro</a>')


def test_renders_link_with_title():
	engine = Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)])

	html = engine.render(
		Link(
			href="/articles/intro",
			title="Start here",
			content=Markup("Intro"),
		)
	)

	assert_eq(
		html,
		'<a href="/articles/intro" title="Start here">Intro</a>',
	)
