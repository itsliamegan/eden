from pathlib import Path
from tempfile import TemporaryDirectory

from luna.test.assertion import assert_eq

from eden.console import Build, New

ROOT = Path(__file__).parent.parent.parent


def test_builds_skeleton_site():
	with TemporaryDirectory() as directory:
		site = Path(directory, "site")
		New(directory=site).run()
		Path(site, "node_modules").symlink_to(Path(ROOT, "node_modules"))
		Path(site, "src", "views", "home.html").write_text("<h1>Intro</h1>")

		Build(directory=site).run()

		assert_eq(Path(site, "public", "index.html").read_text(), "<h1>Intro</h1>")
