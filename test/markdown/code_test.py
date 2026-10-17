from helios.view import Engine, file, memory
from luna.test.assertion import assert_eq

from eden.markdown import Code, VIEWS_DIR


def test_renders_code():
	engine = Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)])

	html = engine.render(Code(language=None, code="eden build\n"))

	assert_eq(html, "<pre><code>eden build\n</code></pre>")


def test_renders_code_with_language():
	engine = Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)])

	html = engine.render(Code(language="python", code="print(1 < 2)\n"))

	assert_eq(
		html,
		'<pre><code class="language-python">print(1 &lt; 2)\n</code></pre>',
	)
