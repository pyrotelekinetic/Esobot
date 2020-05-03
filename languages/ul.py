import asyncio

display_name = "UL (Underload)"
hello_world = "(Hello, world!)S"


async def interpret(program, _, __, stdout):
    try:
        await run(program, [], stdout)
    except Exception as err:
        await stdout.write(type(err).__name__ + ": " + str(err))

def assert_stack_size(stack, size, cmd):
    if len(stack) < size:
        raise Exception(f"The command {cmd} wanted a stack with at least {size} items, but it had {len(stack)} items.")

async def run(prog, stack, stdout):
    depth = 0
    parens_start = 0
    for i, char in enumerate(prog):
        if depth == 0:
            if char == ":":
                assert_stack_size(stack, 1, ":")
                stack.append(stack[-1])
            elif char == "!":
                assert_stack_size(stack, 1, "!")
                stack.pop()
            elif char == "^":
                assert_stack_size(stack, 1, "^")
                await run(stack.pop(), stack, stdout)
            elif char == "~":
                assert_stack_size(stack, 2, "~")
                a = stack.pop()
                b = stack.pop()
                stack.append(a)
                stack.append(b)
            elif char == "*":
                assert_stack_size(stack, 2, "*")
                a = stack.pop()
                b = stack.pop()
                stack.append(b + a)
            elif char == "S":
                assert_stack_size(stack, 1, "S")
                await stdout.write(stack.pop())
                await stdout.flush()
            elif char == "a":
                assert_stack_size(stack, 1, "a")
                stack.append(f"({stack.pop()})")
        if char == "(":
            if depth == 0:
                parens_start = i
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                stack.append(prog[parens_start+1:i])
            elif depth < 0:
                raise Exception("Unmatched ).")
    if depth > 0:
        raise Exception("Unmatched (.")