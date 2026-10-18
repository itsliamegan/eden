from helios.view import Engine, file, memory
from luna.test.assertion import assert_eq
from markupsafe import Markup

from eden.markdown import Heading, VIEWS_DIR


def test_renders_heading():
	engine = Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)])

	html = engine.render(
		Heading(
			level=2,
			id="getting-started",
			text="Getting started",
			content=Markup("Getting <em>started</em>"),
		)
	)

	assert_eq(html, '<h2 id="getting-started">Getting <em>started</em></h2>')


def test_renders_heading_without_id():
	engine = Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)])

	html = engine.render(Heading(level=2, id=None, text="...", content=Markup("...")))

	assert_eq(html, "<h2>...</h2>")
