from shutil import rmtree

def write_site(public_dir, site):
	if public_dir.exists():
		rmtree(public_dir)
	else:
		public_dir.mkdir()

	for document in site.documents:
		write_document(public_dir, document)

def write_document(public_dir, document):
	file = public_dir.joinpath(*document.permalink.components)
	if document.permalink.is_index:
		file = file.joinpath("index.html")
	else:
		file = file.with_suffix(".html")

	file.parent.mkdir(parents=True, exist_ok=True)
	file.write_text(document.contents)
