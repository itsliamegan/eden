from helios.view import Engine, file, memory
from luna.test.assertion import assert_eq

from eden.markdown import Footnote, VIEWS_DIR


def test_renders_footnote():
	engine = Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)])

	html = engine.render(Footnote(number=1, id="quiet"))

	assert_eq(html, '<sup id="fnref-quiet"><a href="#fn-quiet">1</a></sup>')
