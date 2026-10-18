from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from luna.test.assertion import assert_eq, assert_raises

from eden.__main__ import Eden
from eden.commands import New


def test_writes_skeleton_tree():
	with TemporaryDirectory() as directory:
		site = Path(directory, "site")

		New(directory=site).run()

		files = []
		for path in site.rglob("*"):
			if path.is_file():
				files.append(path.relative_to(site).as_posix())
		assert_eq(
			sorted(files),
			[
				".gitignore",
				"package.json",
				"site.toml",
				"src/assets/scripts/main.js",
				"src/assets/styles/main.css",
				"src/views/home.html",
			],
		)
		assert_eq(list(Path(site, "src", "content").iterdir()), [])


def test_fails_when_directory_exists():
	with TemporaryDirectory() as directory:
		with redirect_stderr(StringIO()), assert_raises(SystemExit) as raised:
			Eden.main(["new", directory])

		assert_eq(raised.exception.code, 1)
