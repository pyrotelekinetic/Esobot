import asyncio
from enum import Enum
from functools import reduce

display_name = "λ - Lambda Calculus"
hello_world = "(\\nm.\\fx.n f (m f x)) (\\fx.f x) (\\fx.f (f x))"


async def interpret(program, _, __, stdout):
	depth = 0
	for i in program:
		if i == "(":
			depth += 1
		elif i == ")":
			depth -= 1
		if depth < 0:
			return await stdout.write("Unexpected ).")
	if depth > 0:
		return await stdout.write("Unclosed (.")
	
	try:
		parsed = parse("".join(program.split()))
		result = run(parsed)
		simplified = simplify(result)
		while result != simplified:
			result = simplified
			simplified = simplify(result)
		await stdout.write(pretty(simplified))
		await stdout.flush()
	except Exception as err:
		return await stdout.write(type(err).__name__ + ": " + str(err))

class LC_Expr(Enum):
	var = 0
	apply = 1
	func = 2

def parse(expr):
	if expr[0] == "\\":
		func = {"type": LC_Expr.func, "arg": expr[1]}
		if expr[2] == ".":
			func["body"] = parse(expr[3:])
			return func
		elif expr[2] == "\\":
			raise Exception("Lambdas need a dot to separate their arguments from their body.")
		else:
			func["body"] = parse("\\" + expr[2:])
			return func
	else:
		terms = []
		depth = 0
		begin = 0
		for i, char in enumerate(expr):
			if char == "(":
				if depth == 0:
					begin = i
				depth += 1
			elif char == ")":
				depth -= 1
				if depth == 0:
					terms.append(parse(expr[begin+1:i]))
			elif depth == 0:
				terms.append({"type": LC_Expr.var, "name": char})
		if len(terms) == 0:
			raise Exception("Empty parenthesis not allowed.")
		elif len(terms) == 1:
			return terms[0]
		else:
			return reduce(lambda x, y: {"type": LC_Expr.apply, "func": x, "arg": y}, terms)

def run(ast):
	if ast["type"] == LC_Expr.apply:
		func = run(ast["func"])
		if func["type"] == LC_Expr.var:
			return ast
		arg = run(ast["arg"])
		applied = replace_arg(func["body"], func["arg"], arg)
		return run(applied)
	else:
		return ast

def replace_arg(ast, name, arg):
	if ast["type"] == LC_Expr.var:
		if ast["name"] == name:
			return arg
		else:
			return ast
	elif ast["type"] == LC_Expr.apply:
		func = replace_arg(ast["func"], name, arg)
		arg_ = replace_arg(ast["arg"], name, arg)
		return {"type": LC_Expr.apply, "func": func, "arg": arg_}
	else:
		if ast["arg"] == name:
			return ast
		else:
			return {
				"type": LC_Expr.func,
				"arg": ast["arg"],
				"body": replace_arg(ast["body"], name, arg)
			}

def simplify(ast):
	if ast["type"] == LC_Expr.apply:
		func = simplify(ast["func"])
		arg = simplify(ast["arg"])
		if (
			(ast["func"]["type"] == LC_Expr.func) &
			(ast["arg"]["type"] == LC_Expr.var)
		):
			return replace_arg(func["body"], func["arg"], arg)
		return {"type": LC_Expr.apply, "func": func, "arg": arg}
	elif ast["type"] == LC_Expr.func:
		return {"type": LC_Expr.func, "arg": ast["arg"], "body": simplify(ast["body"])}
	else:
		return ast

def pretty(ast):
	if ast["type"] == LC_Expr.var:
		return ast["name"]
	elif ast["type"] == LC_Expr.apply:
		func = pretty(ast["func"])
		arg = pretty(ast["arg"])
		if ast["arg"]["type"] == LC_Expr.apply:
			arg = "(" + arg + ")"
		return func + " " + arg
	else:
		arg = "\\" + ast["arg"]
		body = pretty(ast["body"])
		if ast["body"]["type"] == LC_Expr.func:
			body = body[2:-1]
		else:
			arg += "."
		return "(" + arg + body + ")"