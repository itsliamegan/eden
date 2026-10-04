from websites.resource import Site


def test_titleizes_name():
	site = Site("blog")

	assert site.title == "Blog"


def test_uses_root_permalink():
	site = Site("blog")

	assert str(site.permalink) == "/"
