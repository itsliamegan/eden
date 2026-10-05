from luna.test.assertion import assert_eq

from eden.inflect import dasherize, titleize


def test_titleizes_single_word():
	name = "about"
	title = titleize(name)

	assert_eq(title, "About")


def test_titleizes_multiple_words():
	name = "contact_us"
	title = titleize(name)

	assert_eq(title, "Contact Us")


def test_dasherizes_single_word():
	name = "about"
	dashed = dasherize(name)

	assert_eq(dashed, "about")


def test_dasherizes_multiple_words():
	name = "contact_us"
	dashed = dasherize(name)

	assert_eq(dashed, "contact-us")
