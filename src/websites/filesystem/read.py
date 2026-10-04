from toml import loads as parse_toml
from ..resource import Site, Collection, Page, Layout
from ..template import compile, formats

def read_site(root_dir):
	src_dir = root_dir.joinpath("src")
	content_dir = src_dir.joinpath("content")
	layouts_dir = src_dir.joinpath("layouts")

	name = root_dir.stem
	site = Site(name)

	for file in layouts_dir.iterdir():
		layout = read_layout(file)
		site.add_layout(layout)

	for entry in content_dir.iterdir():
		if entry.is_dir():
			collection = read_collection(dir=entry, container=site)
			site.add_content(collection)
		else:
			page = read_page(file=entry, container=site)
			site.add_content(page)

	return site

def read_collection(dir, container):
	metadata_file = dir.joinpath("metadata.toml")
	if metadata_file.exists():
		metadata = read_metadata(metadata_file)
	else:
		metadata = {}

	name = dir.stem
	collection = Collection(name, metadata, container)

	for file in dir.iterdir():
		page = read_page(file, container=collection)
		collection.add_content(page)

	return collection

def read_page(file, container):
	name = file.stem
	metadata, template = read_template_parts(file)

	return Page(name, metadata, template, container)

def read_layout(file):
	name = file.stem
	metadata, template = read_template_parts(file)

	return Layout(name, template)

def read_template_parts(file):
	source = file.read_text()
	header, body = split_source_parts(source)

	metadata = parse_toml(header)
	template = compile(body, formats.by_suffix(file), metadata.get("layout"))

	return metadata, template

def read_metadata(file):
	source = file.read_text()
	metadata = parse_toml(source)

	return metadata

def split_source_parts(source):
	parts = source.split("---\n")

	if len(parts) == 1:
		header = ""
		body = parts[0]
	elif len(parts) == 2:
		header = parts[0]
		body = parts[1]

	return header, body
