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
				raise Exception("Can't call unbound variables.")
			arg = run(ast["arg"])
			applied = replace_arg(func["body"], func["arg"], arg)
			return run(applied)
		else:
			return ast
	
	def replace_arg(expr, name, arg):
		if expr["type"] == LC_Expr.var:
			if expr["name"] == name:
				return arg
			else:
				return expr
		elif expr["type"] == LC_Expr.apply:
			func = replace_arg(expr["func"], name, arg)
			arg_ = replace_arg(expr["arg"], name, arg)
			return {"type": LC_Expr.apply, "func": func, "arg": arg_}
		else:
			if expr["arg"] == name:
				return expr
			else:
				return {
					"type": LC_Expr.func,
					"arg": expr["arg"],
					"body": replace_arg(expr["body"], name, arg)
				}
	
	def simplify(expr):
		if expr["type"] == LC_Expr.apply:
			if (
				(expr["func"]["type"] == LC_Expr.func) &
				(expr["arg"]["type"] == LC_Expr.var)
			):
				if expr["func"]["arg"] == expr["arg"]["name"]:
					return expr["func"]["body"]
			return {
				"type": LC_Expr.apply,
				"func": simplify(expr["func"]),
				"arg": simplify(expr["arg"])
			}
		elif expr["type"] == LC_Expr.func:
			return {"type": LC_Expr.func, "arg": expr["arg"], "body": simplify(expr["body"])}
		else:
			return expr
	
	def pretty(expr):
		if expr["type"] == LC_Expr.var:
			return expr["name"]
		elif expr["type"] == LC_Expr.apply:
			func = pretty(expr["func"])
			arg = pretty(expr["arg"])
			if expr["arg"]["type"] == LC_Expr.apply:
				arg = "(" + arg + ")"
			return func + " " + arg
		else:
			arg = "\\" + expr["arg"]
			body = pretty(expr["body"])
			if expr["body"]["type"] == LC_Expr.func:
				body = body[2:-1]
			else:
				arg += "."
			return "(" + arg + body + ")"
	
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