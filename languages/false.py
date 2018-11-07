import asyncio
from enum import Enum

display_name = "False"
hello_world = '"Hello, world!\n"'


async def interpret(program, _, stdin, stdout):
	try:
		stack = []
		ast = parse(program)
		if type(ast) is tuple:
			(__, pos) = ast
			raise Exception(f"Unmatched ] at char {pos}.")
	except Exception as err:
		await stdout.write(type(err).__name__ + ": " + str(err))

class Command(Enum):
	num = 0
	str = 1
	block = 2
	var = 3
	call = 4

def parse(expr):
	ast = []
	i = 0
	while i < len(expr):
		if expr[i].isspace():
			pass
		elif expr[i].isdigit():
			num = ""
			while i < len(expr) and expr[i].isdigit():
				num += expr[i]
				i += 1
			i -= 1
			ast.append((Command.num, num))
		elif expr[i] == "'":
			i += 1
			ast.append((Command.num, ord(expr[i])))
		elif expr[i].islower():
			ast.append((Command.var, expr[i]))
		elif expr[i] == '"':
			i += 1
			begin = i
			end = i
			while expr[i] != '"':
				end += 1
				i += 1
				if not i < len(expr):
					raise Exception(f"Unclosed string at char {str(begin - 1)}")
			ast.append((Command.str, expr[begin:end]))
		elif expr[i] == "[":
			(block, pos) = parse(expr[i+1:])
			i += pos
			ast.append((Command.block, block))
		elif expr[i] == "]":
			return (ast, i + 1)
		elif expr[i] == "{":
			while expr[i] != "}":
				i += 1
		else:
			ast.append((Command.call, expr[i]))
		i += 1
	return ast
