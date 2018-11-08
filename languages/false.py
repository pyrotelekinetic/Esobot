import asyncio
from enum import Enum
import re

display_name = "False"
hello_world = '"Hello, world!\n"'


async def interpret(program, _, stdin, stdout):
	#try:
		stack = []
		vars = []
		ast = parse(program)
		if type(ast) is tuple:
			(__, pos) = ast
			raise Exception(f"Unmatched ] at char {pos}.")
		return await run(ast, stack, vars, stdin, stdout)
	#except Exception as err:
	#	await stdout.write(type(err).__name__ + ": " + str(err))

class Cmd(Enum):
	num = 0
	str = 1
	block = 2
	var = 3
	call = 4

def pretty_type(cmd_type):
	if cmd_type == Cmd.num:
		return "number"
	elif cmd_type == Cmd.str:
		return "string"
	elif cmd_type == Cmd.var:
		return "variable reference"

is_var = re.compile("[a-z]")

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
			ast.append((Cmd.num, int(num)))
		elif expr[i] == "'":
			i += 1
			ast.append((Cmd.num, ord(expr[i])))
		elif is_var.match(expr[i]):
			ast.append((Cmd.var, expr[i]))
		elif expr[i] == '"':
			i += 1
			begin = i
			end = i
			while expr[i] != '"':
				end += 1
				i += 1
				if not i < len(expr):
					raise Exception(f"Unclosed string at char {str(begin - 1)}")
			ast.append((Cmd.str, expr[begin:end]))
		elif expr[i] == "[":
			(block, pos) = parse(expr[i+1:])
			i += pos
			ast.append((Cmd.block, block))
		elif expr[i] == "]":
			return (ast, i + 1)
		elif expr[i] == "{":
			while expr[i] != "}":
				i += 1
		else:
			ast.append((Cmd.call, expr[i]))
		i += 1
	return ast

async def run(ast, stack, vars, stdin, stdout):
	for cmd in ast:
		if cmd[0] == Cmd.str:
			await stdout.write(cmd[1])
		elif cmd[0] != Cmd.call:
			stack += [cmd]
		else:
			if cmd[1] in built_ins.keys():
				built_in = built_ins[cmd[1]]
				assert_min_depth(
					stack, built_in[1],
					f"{built_in[3]} was called when the stack was only {len(stack)} deep while it was required to be at least {built_in[1]} deep."
				)
				if built_in[2] != None:
					types = list(map(lambda x: x[0], stack[-len(built_in[2]):]))
					assert_args(stack, built_in[2], wrong_args(built_in[3], types, built_in[2]))
				(stack, vars) = await built_in[0](stack, vars, stdin, stdout)
			else:
				await stdout.write(f"{cmd[1]} is not a command")
				stack = stack[:-1]
	return (stack, vars)

def assert_args(stack, args, err):
	types = list(map(lambda x: x[0], stack[-len(args):]))
	if types != args:
		raise Exception(err)

def assert_min_depth(stack, depth, err):
	if len(stack) < depth:
		raise Exception(err)

def wrong_args(name, args, expected):
	return f"Passed {english_list(list(map(pretty_type, args)))} to {name} while it required {english_list(list(map(pretty_type, expected)))}."

def english_list(phrases):
	if len(phrases) == 1:
		return f"a {phrases[0]}"
	elif len(phrases) == 2:
		return f"a {phrases[0]} and a {phrases[1]}"
	else:
		previous_phrases = ", ".join(list(map(lambda w: f"a {w}", phrases[:-1])))
		return f"{previous_phrases}, and a {phrases[-1]}"

#####
# STACK
#####

async def dup(stack, vars, _, __):
	stack += [stack[-1]]
	return (stack, vars)

async def drop(stack, vars, _, __):
	return (stack[:-1], vars)

async def swap(stack, vars, _, __):
	x, y = stack[-2], stack[-1]
	return (stack[:-2] + [y, x], vars)

async def rot(stack, vars, _, __):
	x, y, z = stack[-3], stack[-2], stack[-1]
	return (stack[:-3] + [y, z, x], vars)

# \xF8 -> ø
pick_char = "\xF8"

async def pick(stack, vars, _, __):
	_, n = stack[-1]
	assert_min_depth(stack, n, f"Passed {n} to {pick_char} (pick) but the stack was {len(stack)} deep.")
	return (stack[:-1] + [stack[-n-2]], vars)

#####
# ARITHMETIC
#####

async def add(stack, vars, _, __):
	x, y = stack[-2][1], stack[-1][1]
	return (stack[:-2] + [(Cmd.num, x + y)], vars)

async def sub(stack, vars, _, __):
	x, y = stack[-2][1], stack[-1][1]
	return (stack[:-2] + [(Cmd.num, x - y)], vars)

async def mul(stack, vars, _, __):
	x, y = stack[-2][1], stack[-1][1]
	return (stack[:-2] + [(Cmd.num, x * y)], vars)

async def div(stack, vars, _, __):
	x, y = stack[-2][1], stack[-1][1]
	return (stack[:-2] + [(Cmd.num, x / y)], vars)

async def neg(stack, vars, _, __):
	x = stack[-1][1]
	return (stack[:-1] + [(Cmd.num, -x)], vars)

async def bit_and(stack, vars, _, __):
	x, y = stack[-2][1], stack[-1][1]
	return (stack[:-2] + [(Cmd.num, x & y)], vars)

async def bit_or(stack, vars, _, __):
	x, y = stack[-2][1], stack[-1][1]
	return (stack[:-2] + [(Cmd.num, x | y)], vars)

async def bit_not(stack, vars, _, __):
	x = stack[-1][1]
	return (stack[:-1] + [(Cmd.num, ~x)], vars)

#####
# Comparison
#####

async def gt(stack, vars, _, __):
	x, y = stack[-2][1], stack[-1][1]
	return (stack[:-2] + [(Cmd.num, x > y)], vars)

async def eq(stack, vars, _, __):
	x, y = stack[-2][1], stack[-1][1]
	return (stack[:-2] + [(Cmd.num, x == y)], vars)

#####
# Flow control
#####

async def exe(stack, vars, stdin, stdout):
	return await run(stack[-1][1], stack[:-1], vars, stdin, stdout)

async def cond(stack, vars, stdin, stdout):
	pred, if_true = stack[-2][1], stack[-1][1]
	if pred:
		return await run(stack[-1][1], stack[:-2], vars, stdin, stdout)
	return (stack[:-2], vars)

# \xDF -> ß
built_ins = {
	# Stack
	"$": (dup, 1, None, "$ (dup)"),
	"%": (drop, 1, None, "% (drop)"),
	"\\": (swap, 2, None, "\\ (swap)"),
	"@": (rot, 3, None, "@ (rot)"),
	pick_char: (pick, 1, [Cmd.num], f"{pick_char} (pick)"),
	
	# Arithmetic
	"+": (add, 2, [Cmd.num, Cmd.num], "+ (plus)"),
	"-": (sub, 2, [Cmd.num, Cmd.num], "- (minus)"),
	"*": (mul, 2, [Cmd.num, Cmd.num], "* (times)"),
	"/": (div, 2, [Cmd.num, Cmd.num], "/ (divide)"),
	"_": (neg, 1, [Cmd.num], "_ (negate)"),
	"&": (bit_and, 2, [Cmd.num, Cmd.num], "& (and)"),
	"|": (bit_or, 2, [Cmd.num, Cmd.num], "| (or)"),
	"~": (bit_not, 1, [Cmd.num], "~ (not)"),
	
	# Comparison
	">": (gt, 2, [Cmd.num, Cmd.num], "> (greater than)"),
	"=": (eq, 2, [Cmd.num, Cmd.num], "= (equal)"),
	
	# Flow control
	"!": (exe, 1, [Cmd.block], "! (execute)"),
	"?": (cond, 2, [Cmd.num, Cmd.block], "? (conditional execute)")
}