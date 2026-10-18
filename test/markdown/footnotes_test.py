from helios.view import Engine, file, memory
from luna.test.assertion import assert_eq
from markupsafe import Markup

from eden.markdown import Footnotes, Note, VIEWS_DIR


def test_renders_footnotes():
	engine = Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)])

	html = engine.render(
		Footnotes(
			notes=[
				Note(1, "source", Markup("<p>From the manual.</p>")),
				Note(2, "aside", Markup("<p>An aside.</p>")),
			]
		)
	)

	assert_eq(
		html,
		'<section class="footnotes">\n<ol>\n'
		'<li id="fn-source">\n<p>From the manual.</p>\n<a href="#fnref-source">↩</a>\n</li>\n'
		'<li id="fn-aside">\n<p>An aside.</p>\n<a href="#fnref-aside">↩</a>\n</li>\n'
		"</ol>\n</section>",
	)
