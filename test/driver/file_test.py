from pathlib import Path
from tempfile import TemporaryDirectory

from helios.assets import Manifest
from luna.test.assertion import assert_eq, assert_not, assert_raises, assert_that

from eden.content import Collection, ContentError, ContentPath, Item, Items
from eden.document import Document
from eden.driver import DuplicateFileError, file


def test_reads_top_level_items():
	with TemporaryDirectory() as directory:
		content = Path(directory, "src", "content")
		content.mkdir(parents=True)
		content.joinpath("about.md").write_text("About")
		content.joinpath("info.toml").write_text('title = "Info"')

		items = file.Driver(Path(directory)).items()

		assert_eq(
			items,
			[
				Item.markdown(ContentPath.parse("about"), "About"),
				Item.toml(ContentPath.parse("info"), 'title = "Info"'),
			],
		)


def test_reads_item_text_and_fields():
	with TemporaryDirectory() as directory:
		content = Path(directory, "src", "content")
		content.mkdir(parents=True)
		content.joinpath("about.md").write_text('+++\ntitle = "About"\n+++\nHello')

		items = file.Driver(Path(directory)).items()

		assert_eq(items[0].fields, {"title": "About"})
		assert_eq(items[0].text, "Hello")


def test_reads_toml_item_fields():
	with TemporaryDirectory() as directory:
		content = Path(directory, "src", "content")
		content.mkdir(parents=True)
		content.joinpath("info.toml").write_text('title = "Info"')

		items = file.Driver(Path(directory)).items()

		assert_eq(items[0].fields, {"title": "Info"})
		assert_eq(items[0].text, "")


def test_reads_items_in_order_of_name():
	with TemporaryDirectory() as directory:
		content = Path(directory, "src", "content")
		content.mkdir(parents=True)
		content.joinpath("outro.md").write_text("")
		content.joinpath("intro.md").write_text("")
		content.joinpath("about.md").write_text("")

		items = file.Driver(Path(directory)).items()

		assert_eq(
			items,
			[
				Item.markdown(ContentPath.parse("about"), ""),
				Item.markdown(ContentPath.parse("intro"), ""),
				Item.markdown(ContentPath.parse("outro"), ""),
			],
		)


def test_skips_hidden_files_and_directories():
	with TemporaryDirectory() as directory:
		content = Path(directory, "src", "content")
		content.joinpath(".drafts").mkdir(parents=True)
		content.joinpath(".drafts", "intro.md").write_text("")
		content.joinpath(".DS_Store").write_text("")
		content.joinpath("about.md").write_text("")

		driver = file.Driver(Path(directory))

		assert_eq(driver.items(), [Item.markdown(ContentPath.parse("about"), "")])
		assert_eq(driver.collections(), [])


def test_skips_hidden_files_in_collection():
	with TemporaryDirectory() as directory:
		articles = Path(directory, "src", "content", "articles")
		articles.mkdir(parents=True)
		articles.joinpath(".DS_Store").write_text("")
		articles.joinpath("intro.md").write_text("")

		collections = file.Driver(Path(directory)).collections()

		assert_eq(
			collections,
			[
				Collection(
					ContentPath.parse("articles"),
					Items([Item.markdown(ContentPath.parse("articles/intro"), "")]),
				)
			],
		)


def test_reads_collection_items_in_order_of_name():
	with TemporaryDirectory() as directory:
		articles = Path(directory, "src", "content", "articles")
		articles.mkdir(parents=True)
		articles.joinpath("outro.md").write_text("")
		articles.joinpath("intro.md").write_text("")

		collection = file.Driver(Path(directory)).collections()[0]

		assert_eq(
			list(collection),
			[
				Item.markdown(ContentPath.parse("articles/intro"), ""),
				Item.markdown(ContentPath.parse("articles/outro"), ""),
			],
		)


def test_reads_items_in_order_of_name_not_file_name():
	with TemporaryDirectory() as directory:
		articles = Path(directory, "src", "content", "articles")
		articles.mkdir(parents=True)
		articles.joinpath("intro-2.md").write_text("")
		articles.joinpath("intro.md").write_text("")

		collection = file.Driver(Path(directory)).collections()[0]

		assert_eq(
			list(collection),
			[
				Item.markdown(ContentPath.parse("articles/intro"), ""),
				Item.markdown(ContentPath.parse("articles/intro-2"), ""),
			],
		)


def test_reads_collection_path():
	with TemporaryDirectory() as directory:
		articles = Path(directory, "src", "content", "articles")
		articles.mkdir(parents=True)

		collection = file.Driver(Path(directory)).collections()[0]

		assert_eq(collection.path, ContentPath.parse("articles"))
		assert_eq(collection.index, None)


def test_reads_nested_collections_as_flat_entries():
	with TemporaryDirectory() as directory:
		content = Path(directory, "src", "content")
		content.joinpath("articles", "drafts").mkdir(parents=True)
		content.joinpath("articles", "intro.md").write_text("")
		content.joinpath("articles", "drafts", "outro.md").write_text("")
		content.joinpath("links").mkdir()

		collections = file.Driver(Path(directory)).collections()

		assert_eq(
			collections,
			[
				Collection(
					ContentPath.parse("articles"),
					Items([Item.markdown(ContentPath.parse("articles/intro"), "")]),
				),
				Collection(
					ContentPath.parse("articles/drafts"),
					Items(
						[Item.markdown(ContentPath.parse("articles/drafts/outro"), "")]
					),
				),
				Collection(ContentPath.parse("links"), Items([])),
			],
		)


def test_reads_index_item_beside_collection():
	with TemporaryDirectory() as directory:
		content = Path(directory, "src", "content")
		content.joinpath("articles").mkdir(parents=True)
		content.joinpath("articles.md").write_text("Articles")
		content.joinpath("articles", "intro.md").write_text("")

		collection = file.Driver(Path(directory)).collections()[0]

		assert_eq(collection.index, Item.markdown(ContentPath.parse("articles"), ""))


def test_reads_toml_index_item():
	with TemporaryDirectory() as directory:
		content = Path(directory, "src", "content")
		content.joinpath("articles").mkdir(parents=True)
		content.joinpath("articles.toml").write_text('title = "Articles"')

		collection = file.Driver(Path(directory)).collections()[0]

		assert_eq(collection.index, Item.toml(ContentPath.parse("articles"), ""))


def test_leaves_index_item_out_of_top_level_items():
	with TemporaryDirectory() as directory:
		content = Path(directory, "src", "content")
		content.joinpath("articles").mkdir(parents=True)
		content.joinpath("articles.md").write_text("")
		content.joinpath("about.md").write_text("")

		items = file.Driver(Path(directory)).items()

		assert_eq(items, [Item.markdown(ContentPath.parse("about"), "")])


def test_leaves_index_item_out_of_collection_items():
	with TemporaryDirectory() as directory:
		articles = Path(directory, "src", "content", "articles")
		articles.joinpath("intro").mkdir(parents=True)
		articles.joinpath("intro.md").write_text("")
		articles.joinpath("outro.md").write_text("")

		collections = file.Driver(Path(directory)).collections()

		assert_eq(
			list(collections[0]),
			[Item.markdown(ContentPath.parse("articles/outro"), "")],
		)


def test_reads_index_item_beside_nested_collection():
	with TemporaryDirectory() as directory:
		articles = Path(directory, "src", "content", "articles")
		articles.joinpath("drafts").mkdir(parents=True)
		articles.joinpath("drafts.md").write_text("")

		collections = file.Driver(Path(directory)).collections()

		assert_eq(collections[0].index, None)
		assert_eq(
			collections[1].index,
			Item.markdown(ContentPath.parse("articles/drafts"), ""),
		)


def test_rejects_stray_file_in_content():
	with TemporaryDirectory() as directory:
		content = Path(directory, "src", "content")
		content.mkdir(parents=True)
		content.joinpath("about.txt").write_text("")

		with assert_raises(ContentError):
			file.Driver(Path(directory)).items()


def test_rejects_stray_file_in_collection():
	with TemporaryDirectory() as directory:
		articles = Path(directory, "src", "content", "articles")
		articles.mkdir(parents=True)
		articles.joinpath("intro.html").write_text("")

		with assert_raises(ContentError):
			file.Driver(Path(directory)).collections()


def test_rejects_stray_file_beside_collection():
	with TemporaryDirectory() as directory:
		content = Path(directory, "src", "content")
		content.joinpath("articles").mkdir(parents=True)
		content.joinpath("articles.txt").write_text("")

		with assert_raises(ContentError):
			file.Driver(Path(directory)).collections()


def test_rejects_file_without_extension():
	with TemporaryDirectory() as directory:
		content = Path(directory, "src", "content")
		content.mkdir(parents=True)
		content.joinpath("about").write_text("")

		with assert_raises(ContentError):
			file.Driver(Path(directory)).items()


def test_rejects_items_with_one_name():
	with TemporaryDirectory() as directory:
		content = Path(directory, "src", "content")
		content.mkdir(parents=True)
		content.joinpath("about.md").write_text("")
		content.joinpath("about.toml").write_text("")

		with assert_raises(ContentError):
			file.Driver(Path(directory)).items()


def test_rejects_items_with_one_name_in_collection():
	with TemporaryDirectory() as directory:
		articles = Path(directory, "src", "content", "articles")
		articles.mkdir(parents=True)
		articles.joinpath("intro.md").write_text("")
		articles.joinpath("intro.toml").write_text("")

		with assert_raises(ContentError):
			file.Driver(Path(directory)).collections()


def test_rejects_index_item_in_collection():
	with TemporaryDirectory() as directory:
		articles = Path(directory, "src", "content", "articles")
		articles.mkdir(parents=True)
		articles.joinpath("index.md").write_text("")

		with assert_raises(ContentError):
			file.Driver(Path(directory)).collections()


def test_rejects_index_item_at_top_level():
	with TemporaryDirectory() as directory:
		content = Path(directory, "src", "content")
		content.mkdir(parents=True)
		content.joinpath("index.md").write_text("")

		with assert_raises(ContentError):
			file.Driver(Path(directory)).items()


def test_reads_no_items_without_content():
	with TemporaryDirectory() as directory:
		assert_eq(file.Driver(Path(directory)).items(), [])


def test_reads_no_collections_without_content():
	with TemporaryDirectory() as directory:
		assert_eq(file.Driver(Path(directory)).collections(), [])


def test_reads_no_views_without_views_directory():
	with TemporaryDirectory() as directory:
		assert_eq(file.Driver(Path(directory)).views().names(), [])


def test_reads_views_from_views_directory():
	with TemporaryDirectory() as directory:
		root = Path(directory)
		root.joinpath("src", "views", "articles").mkdir(parents=True)
		root.joinpath("src", "views", "articles", "show.html").write_text("Show")

		driver = file.Driver(root).views()

		assert_eq(driver.names(), ["articles/show"])


def test_empties_public():
	with TemporaryDirectory() as directory:
		public = Path(directory, "public")
		public.joinpath("articles").mkdir(parents=True)
		public.joinpath("articles", "intro.html").write_text("")
		public.joinpath("index.html").write_text("")
		public.joinpath(".nojekyll").write_text("")

		file.Driver(Path(directory)).empty()

		assert_that(public.is_dir())
		assert_eq(list(public.iterdir()), [])


def test_empties_missing_public():
	with TemporaryDirectory() as directory:
		file.Driver(Path(directory)).empty()

		assert_that(Path(directory, "public").is_dir())
		assert_eq(list(Path(directory, "public").iterdir()), [])


def test_compiles_no_entry_points_to_empty_manifest():
	with TemporaryDirectory() as directory:
		manifest = file.Driver(Path(directory)).compile(
			[],
			[],
			minify=False,
			sourcemap=False,
		)

		assert_eq(manifest, Manifest({}, {}))


def test_compiles_no_entry_points_to_empty_assets():
	with TemporaryDirectory() as directory:
		assets = Path(directory, "public", "assets")
		assets.mkdir(parents=True)
		assets.joinpath("old.js").write_text("")

		file.Driver(Path(directory)).compile([], [], minify=False, sourcemap=False)

		assert_that(assets.is_dir())
		assert_eq(list(assets.iterdir()), [])


def test_writes_root_to_index_file():
	with TemporaryDirectory() as directory:
		file.Driver(Path(directory)).write([Document("/", "Home")])

		assert_eq(Path(directory, "public", "index.html").read_text(), "Home")


def test_writes_index_path_to_index_file_in_directory():
	with TemporaryDirectory() as directory:
		file.Driver(Path(directory)).write([Document("/articles/", "Articles")])

		public = Path(directory, "public")
		assert_eq(public.joinpath("articles", "index.html").read_text(), "Articles")


def test_writes_path_to_html_file():
	with TemporaryDirectory() as directory:
		file.Driver(Path(directory)).write([Document("/about", "About")])

		assert_eq(Path(directory, "public", "about.html").read_text(), "About")


def test_writes_nested_path_to_html_file():
	with TemporaryDirectory() as directory:
		file.Driver(Path(directory)).write([Document("/articles/intro", "Intro")])

		public = Path(directory, "public")
		assert_eq(public.joinpath("articles", "intro.html").read_text(), "Intro")


def test_writes_dotted_path_to_file_itself():
	with TemporaryDirectory() as directory:
		file.Driver(Path(directory)).write([Document("/feed.xml", "Feed")])

		assert_eq(Path(directory, "public", "feed.xml").read_text(), "Feed")


def test_writes_dot_in_name_to_file_itself():
	with TemporaryDirectory() as directory:
		file.Driver(Path(directory)).write([Document("/v1.2", "Version")])

		assert_eq(Path(directory, "public", "v1.2").read_text(), "Version")


def test_writes_dotted_nested_path_to_file_itself():
	with TemporaryDirectory() as directory:
		file.Driver(Path(directory)).write([Document("/articles/feed.xml", "Feed")])

		public = Path(directory, "public")
		assert_eq(public.joinpath("articles", "feed.xml").read_text(), "Feed")


def test_writes_every_document():
	with TemporaryDirectory() as directory:
		file.Driver(Path(directory)).write(
			[Document("/about", "About"), Document("/info", "Info")]
		)

		public = Path(directory, "public")
		assert_eq(public.joinpath("about.html").read_text(), "About")
		assert_eq(public.joinpath("info.html").read_text(), "Info")


def test_rejects_documents_that_write_one_file():
	with TemporaryDirectory() as directory:
		driver = file.Driver(Path(directory))

		with assert_raises(DuplicateFileError):
			driver.write([Document("/about", "About"), Document("/about.html", "")])


def test_rejects_document_over_existing_file():
	with TemporaryDirectory() as directory:
		public = Path(directory, "public")
		public.mkdir()
		public.joinpath("about.html").write_text("Old")

		with assert_raises(DuplicateFileError):
			file.Driver(Path(directory)).write([Document("/about", "About")])

		assert_eq(public.joinpath("about.html").read_text(), "Old")


def test_copies_static_files():
	with TemporaryDirectory() as directory:
		static = Path(directory, "src", "static")
		static.mkdir(parents=True)
		static.joinpath("robots.txt").write_text("Robots")

		file.Driver(Path(directory)).copy()

		assert_eq(Path(directory, "public", "robots.txt").read_text(), "Robots")


def test_copies_nested_static_files():
	with TemporaryDirectory() as directory:
		static = Path(directory, "src", "static", "images", "icons")
		static.mkdir(parents=True)
		static.joinpath("logo.svg").write_text("Logo")

		file.Driver(Path(directory)).copy()

		public = Path(directory, "public")
		assert_eq(public.joinpath("images", "icons", "logo.svg").read_text(), "Logo")


def test_copies_hidden_static_files():
	with TemporaryDirectory() as directory:
		static = Path(directory, "src", "static")
		static.joinpath(".well-known").mkdir(parents=True)
		static.joinpath(".well-known", "security.txt").write_text("Security")
		static.joinpath(".nojekyll").write_text("")

		file.Driver(Path(directory)).copy()

		public = Path(directory, "public")
		assert_eq(
			public.joinpath(".well-known", "security.txt").read_text(), "Security"
		)
		assert_that(public.joinpath(".nojekyll").is_file())


def test_copies_no_static_files_without_static_directory():
	with TemporaryDirectory() as directory:
		file.Driver(Path(directory)).copy()

		assert_not(Path(directory, "public").exists())


def test_rejects_static_file_over_page():
	with TemporaryDirectory() as directory:
		static = Path(directory, "src", "static")
		static.mkdir(parents=True)
		static.joinpath("about.html").write_text("Static")
		driver = file.Driver(Path(directory))
		driver.write([Document("/about", "About")])

		with assert_raises(DuplicateFileError):
			driver.copy()

		assert_eq(Path(directory, "public", "about.html").read_text(), "About")


def test_rejects_static_file_over_compiled_asset():
	with TemporaryDirectory() as directory:
		static = Path(directory, "src", "static", "assets")
		static.mkdir(parents=True)
		static.joinpath("main.js").write_text("Static")
		public = Path(directory, "public", "assets")
		public.mkdir(parents=True)
		public.joinpath("main.js").write_text("Compiled")

		with assert_raises(DuplicateFileError):
			file.Driver(Path(directory)).copy()


def test_rejects_page_over_static_file():
	with TemporaryDirectory() as directory:
		static = Path(directory, "src", "static")
		static.mkdir(parents=True)
		static.joinpath("about.html").write_text("Static")
		driver = file.Driver(Path(directory))
		driver.copy()

		with assert_raises(DuplicateFileError):
			driver.write([Document("/about", "About")])
