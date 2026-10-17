from helios.view import Engine, file, memory
from luna.test.assertion import assert_eq
from markupsafe import Markup

from eden.markdown import Footnotes, Note, VIEWS_DIR


def test_renders_footnotes():
	engine = Engine(memory.Driver({}), fallbacks=[file.Driver(VIEWS_DIR)])

	html = engine.render(
		Footnotes(
			notes=[
				Note(1, "quiet", Markup("<p>A still lake.</p>")),
				Note(2, "dawn", Markup("<p>Before sunrise.</p>")),
			]
		)
	)

	assert_eq(
		html,
		'<section class="footnotes">\n<ol>\n'
		'<li id="fn-quiet">\n<p>A still lake.</p>\n<a href="#fnref-quiet">↩</a>\n</li>\n'
		'<li id="fn-dawn">\n<p>Before sunrise.</p>\n<a href="#fnref-dawn">↩</a>\n</li>\n'
		"</ol>\n</section>",
	)
