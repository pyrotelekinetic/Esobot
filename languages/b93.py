import asyncio
from enum import Enum, auto
import random

display_name = "B93 (Befunge-93)"
hello_world = '"!dlroW ,olleH">:#,_@ (Put this in a code block.)'


async def interpret(program, _, stdin, stdout):
    try:
        program = program.splitlines()
        if program[0] == "```":
            program = program[1:-1]
        longest_line = max(list(map(len, program)))
        program = list(map(
            lambda l: l.ljust(longest_line), # Make all lines the same length.
            program
        ))
        width = prog_width(program)
        height = prog_height(program)
        ip = Ip(0, 0, Dir.right)
        stack = []
        while True:
            await asyncio.sleep(0)
            instr = program[ip.y][ip.x]
            if instr == "@":
                break
            elif instr == '"':
                ip = ip.move(width, height)
                while program[ip.y][ip.x] != '"':
                    stack += [ord(program[ip.y][ip.x])]
                    ip = ip.move(width, height)
            else:
                if instr in commands.keys():
                    command = commands[instr]
                    if len(stack) < command.args:
                        zeros = [0] * (command.args - len(stack))
                        stack = zeros + stack
                    stack, ip, program = await command.impl(
                        stack, ip, program,
                        stdin, stdout
                    )
            ip = ip.move(width, height)
        return stack
    except Exception as err:
        await stdout.write(type(err).__name__ + ": " + str(err))

def prog_width(program):
    return len(program[0])

def prog_height(program):
    return len(program)

class Dir(Enum):
    right = auto()
    left = auto()
    up = auto()
    down = auto()
    
    def to_pos(self):
        if self == self.right:
            return (1, 0)
        elif self == self.left:
            return (-1, 0)
        elif self == self.up:
            return (0, -1)
        elif self == self.down:
            return (0, 1)

class Ip():
    def __init__(self, x, y, dir):
        self.x = x
        self.y = y
        self.dir = dir
    
    def change_dir(self, dir):
        return Ip(self.x, self.y, dir)
    
    def move(self, width, height):
        move_x, move_y = self.dir.to_pos()
        x = self.x + move_x
        y = self.y + move_y
        # Wrap pointer around the program.
        if x < 0:
            x = width - 1
        elif x >= width:
            x = 0
        if y < 0:
            y = height - 1
        elif y >= height:
            y = 0
        return Ip(x, y, self.dir)

#####
# NUMBERS
#####

async def zero(stack, ip, program, _, __):
    return (stack + [0], ip, program)

async def one(stack, ip, program, _, __):
    return (stack + [1], ip, program)

async def two(stack, ip, program, _, __):
    return (stack + [2], ip, program)

async def three(stack, ip, program, _, __):
    return (stack + [3], ip, program)

async def four(stack, ip, program, _, __):
    return (stack + [4], ip, program)

async def five(stack, ip, program, _, __):
    return (stack + [5], ip, program)

async def six(stack, ip, program, _, __):
    return (stack + [6], ip, program)

async def seven(stack, ip, program, _, __):
    return (stack + [7], ip, program)

async def eight(stack, ip, program, _, __):
    return (stack + [8], ip, program)

async def nine(stack, ip, program, _, __):
    return (stack + [9], ip, program)

#####
# MATH
#####

async def add(stack, ip, program, _, __):
    a, b = stack[-2], stack[-1]
    return (stack[:-2] + [a + b], ip, program)

async def sub(stack, ip, program, _, __):
    a, b = stack[-2], stack[-1]
    return (stack[:-2] + [a - b], ip, program)

async def mul(stack, ip, program, _, __):
    a, b = stack[-2], stack[-1]
    return (stack[:-2] + [a * b], ip, program)

async def div(stack, ip, program, _, __):
    a, b = stack[-2], stack[-1]
    return (stack[:-2] + [a / b], ip, program)

async def mod(stack, ip, program, _, __):
    a, b = stack[-2], stack[-1]
    return (stack[:-2] + [a % b], ip, program)

async def _not(stack, ip, program, _, __):
    a = stack[-1]
    return (stack[:-1] + [int(not a)], ip, program)

async def gt(stack, ip, program, _, __):
    a, b = stack[-2], stack[-1]
    return (stack[:-2] + [int(a > b)], ip, program)

#####
# MOVEMENT
#####

async def right(stack, ip, program, _, __):
    return (stack, ip.change_dir(Dir.right), program)

async def left(stack, ip, program, _, __):
    return (stack, ip.change_dir(Dir.left), program)

async def up(stack, ip, program, _, __):
    return (stack, ip.change_dir(Dir.up), program)

async def down(stack, ip, program, _, __):
    return (stack, ip.change_dir(Dir.down), program)

async def move_random(stack, ip, program, _, __):
    ip = ip.change_dir(random.choice(list(Dir)))
    return (stack, ip, program)

async def horiz_if(stack, ip, program, _, __):
    a = stack[-1]
    if a:
        ip = ip.change_dir(Dir.left)
    else:
        ip = ip.change_dir(Dir.right)
    return (stack[:-1], ip, program)

async def vert_if(stack, ip, program, _, __):
    a = stack[-1]
    if a:
        ip = ip.change_dir(Dir.up)
    else:
        ip = ip.change_dir(Dir.down)
    return (stack[:-1], ip, program)

async def skip(stack, ip, program, _, __):
    ip = ip.move(prog_width(program), prog_height(program))
    return (stack, ip, program)

#####
# STACK
#####

async def dup(stack, ip, program, _, __):
    a = stack[-1]
    return (stack + [a], ip, program)

async def swap(stack, ip, program, _, __):
    a, b = stack[-2], stack[-1]
    return (stack[:-2] + [b, a], ip, program)

async def drop(stack, ip, program, _, __):
    return (stack[:-1], ip, program)

#####
# I/O
#####

async def print_num(stack, ip, program, _, stdout):
    await stdout.write(str(stack[-1]))
    return (stack[:-1], ip, program)

async def print_char(stack, ip, program, _, stdout):
    await stdout.write(chr(stack[-1]))
    return (stack[:-1], ip, program)

async def input_num(stack, ip, program, stdin, _):
    num = int(await stdin.readline())
    return (stack + [num], ip, program)

async def input_char(stack, ip, program, stdin, _):
    char = ord(await stdin.read(1))
    return (stack + [char], ip, program)

#####
# STATE
#####

async def get(stack, ip, program, _, __):
    x, y = stack[-2], stack[-1]
    width = prog_width(program)
    height = prog_height(program)
    if x < 0:
        return (stack + [0], ip, program)
    elif x >= width:
        return (stack + [0], ip, program)
    elif y < 0:
        return (stack + [0], ip, program)
    elif y >= height:
        return (stack + [0], ip, program)
    return (stack[:-2] + [ord(program[y][x])], ip, program)

async def put(stack, ip, program, _, __):
    char, x, y = chr(stack[-3]), stack[-2], stack[-1]
    row = program[y][:x] + char + program[y][x+1:]
    program = program[:y] + [row] + program[y+1:]
    return (stack[:-3], ip, program)

class Command():
    def __init__(self, impl, args, name):
        self.impl = impl
        self.args = args
        self.name = name

commands = {
    # Numbers
    "0": Command(zero, 0, "0 (push zero)"),
    "1": Command(one, 0, "1 (push one)"),
    "2": Command(two, 0, "2 (push two)"),
    "3": Command(three, 0, "3 (push three)"),
    "4": Command(four, 0, "4 (push four)"),
    "5": Command(five, 0, "5 (push five)"),
    "6": Command(six, 0, "6 (push six)"),
    "7": Command(seven, 0, "7 (push seven)"),
    "8": Command(eight, 0, "8 (push eight)"),
    "9": Command(nine, 0, "9 (push nine)"),
    
    # Math
    "+": Command(add, 2, "+ (plus)"),
    "-": Command(sub, 2, "- (minus)"),
    "*": Command(mul, 2, "* (times)"),
    "/": Command(div, 2, "/ (divide)"),
    "%": Command(mod, 2, "% (modulo)"),
    "!": Command(_not, 1, "! (not)"),
    "`": Command(gt, 2, "` (greater than)"),
    
    # Movement
    ">": Command(right, 0, "> (point right)"),
    "<": Command(left, 0, "< (point left)"),
    "^": Command(up, 0, "^ (point up)"),
    "v": Command(down, 0, "v (point down)"),
    "?": Command(move_random, 0, "? (random direction)"),
    "_": Command(horiz_if, 1, "_ (horizontal if)"),
    "|": Command(vert_if, 1, "_ (vertical if)"),
    "#": Command(skip, 0, "# (skip next)"),
    
    # Stack
    ":": Command(dup, 1, ": (dup)"),
    "\\": Command(swap, 2, "\\ (swap)"),
    "$": Command(drop, 1, "$ (drop)"),
    
    # I/O
    ".": Command(print_num, 1, ". (print integer)"),
    ",": Command(print_char, 1, ", (print character)"),
    "&": Command(input_num, 0, "& (get integer)"),
    "~": Command(input_char, 0, "~ (get character)"),
    
    # State
    "g": Command(get, 2, "g (get from program)"),
    "p": Command(put, 3, "p (put in program)")
}