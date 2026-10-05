from luna.test.assertion import assert_eq

from eden.resource import Site


def test_titleizes_name():
	site = Site("blog")

	assert_eq(site.title, "Blog")


def test_uses_root_permalink():
	site = Site("blog")

	assert_eq(str(site.permalink), "/")
