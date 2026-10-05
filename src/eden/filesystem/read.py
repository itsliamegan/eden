from pathlib import Path
from typing import Any

from toml import loads as parse_toml

from ..resource import Collection, Layout, Page, Site
from ..template import Template
from ..template.format import Format


def read_site(root_dir: Path) -> Site:
	src_dir = root_dir.joinpath("src")
	content_dir = src_dir.joinpath("content")
	layouts_dir = src_dir.joinpath("layouts")

	name = root_dir.stem
	site = Site(name)

	for file in layouts_dir.iterdir():
		layout = read_layout(file)
		site.add_layout(layout)

	for path in content_dir.iterdir():
		if path.is_dir():
			collection = read_collection(dir=path, container=site)
			site.add_content(collection)
		elif path.stem == "index":
			site.index = read_index_page(file=path, container=site)
		elif content_dir.joinpath(path.stem).is_dir():
			# The collection of the same name reads this file as its index page.
			pass
		else:
			page = read_entry_page(file=path, container=site)
			site.add_content(page)

	return site


def read_collection(dir: Path, container: Site) -> Collection:
	metadata_file = dir.joinpath("metadata.toml")
	if metadata_file.exists():
		metadata = read_metadata(metadata_file)
	else:
		metadata = {}

	name = dir.stem
	collection = Collection(name, metadata, container)

	for file in dir.parent.iterdir():
		if file.is_file() and file.stem == dir.name:
			collection.index = read_index_page(file, container=collection)

	for file in dir.iterdir():
		if file.stem == "index":
			index_path = file.relative_to(dir.parent)
			raise ValueError(f"Collection {name} contains an index page: {index_path}")

		page = read_entry_page(file, container=collection)
		collection.add_content(page)

	return collection


def read_entry_page(file: Path, container: Site | Collection) -> Page:
	name = file.stem
	metadata, template = read_template_parts(file)

	return Page.entry(name, metadata, template, container)


def read_index_page(file: Path, container: Site | Collection) -> Page:
	name = file.stem
	metadata, template = read_template_parts(file)

	return Page.index(name, metadata, template, container)


def read_layout(file: Path) -> Layout:
	name = file.stem
	_metadata, template = read_template_parts(file)

	return Layout(name, template)


def read_template_parts(file: Path) -> tuple[dict[str, Any], Template]:
	source = file.read_text()
	header, body = split_source_parts(source)

	metadata = parse_toml(header)
	template = Template.compile(
		body,
		Format.for_file(file),
		parent=metadata.get("layout"),
	)

	return metadata, template


def read_metadata(file: Path) -> dict[str, Any]:
	source = file.read_text()
	metadata = parse_toml(source)

	return metadata


def split_source_parts(source: str) -> tuple[str, str]:
	parts = source.split("---\n", 1)

	if len(parts) == 1:
		header = ""
		body = parts[0]
	else:
		header = parts[0]
		body = parts[1]

	return header, body
