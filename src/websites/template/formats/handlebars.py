import pybars

compiler = pybars.Compiler()

def compile(source):
	return compiler.compile(source)

def execute(compiled, runtime):
	locals = runtime.locals | {"content": safe(runtime.content)}

	runtime.content = compiled(
		locals,
		helpers={
			"content-for": handlebarsify(runtime.content_for),
		},
	)

def handlebarsify(helper):
	def wrapped_helper(context, *args, **kwargs):
		args = list(args)

		if was_called_as_block_helper(args):
			options = args.pop(0)
			content = options["fn"](context)
			args.append(content)

		value = helper(*args, **kwargs)
		return safe(value)

	return wrapped_helper

def was_called_as_block_helper(args):
	return len(args) > 0 and isinstance(args[0], dict) and "fn" in args[0]

def safe(value):
	return pybars.strlist([str(value)])
