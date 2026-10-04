from pathlib import Path
from textwrap import dedent

def create(name, minimal=False):
	working_dir = Path.cwd()
	root_dir = working_dir.joinpath(name)
	public_dir = root_dir.joinpath("public")
	src_dir = root_dir.joinpath("src")
	content_dir = src_dir.joinpath("content")
	layouts_dir = src_dir.joinpath("layouts")

	root_dir.mkdir()
	public_dir.mkdir()
	src_dir.mkdir()
	content_dir.mkdir()
	layouts_dir.mkdir()

	if not minimal:
		main_layout_file = layouts_dir.joinpath("main.hbs")
		index_page_file = content_dir.joinpath("index.hbs")

		main_layout_file.write_text(
			dedent("""\
				<!doctype html>
				<html lang="en">
					<head>
						<meta charset="utf-8">
						<meta name="viewport" content="width=device-width,initial-scale=1">

						<title>{{site.title}}</title>
					</head>

					<body>
						{{content}}
					</body>
				</html>
			""")
		)
		index_page_file.write_text(
			dedent("""\
				layout = "main"
				---
				<h1>{{site.title}}</h1>
			""")
		)
