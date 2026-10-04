from cmarkgfm import github_flavored_markdown_to_html as gfm_to_html

def compile(source):
	return gfm_to_html(source)

def execute(compiled, runtime):
	runtime.content = compiled
