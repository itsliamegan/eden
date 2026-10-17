from helios.view import Engine, file, memory
from luna.test.assertion import assert_eq

from eden.markdown import Image, VIEWS_DIR


def test_renders_image():
	engine = Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)])

	html = engine.render(Image(src="/lake.jpg", alt="A lake", title=None))

	assert_eq(html, '<img src="/lake.jpg" alt="A lake">')


def test_renders_image_with_title():
	engine = Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)])

	html = engine.render(Image(src="/lake.jpg", alt="A lake", title="At dawn"))

	assert_eq(html, '<img src="/lake.jpg" alt="A lake" title="At dawn">')
