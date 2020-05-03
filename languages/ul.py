import asyncio

display_name = "UL (Underload)"
hello_world = "(Hello, world!)S"


async def interpret(program, _, __, stdout):
    try:
        await run(program, [], [[""]], stdout)
    except Exception as err:
        await stdout.write(type(err).__name__ + ": " + str(err))

def assert_stack_size(stack, size, cmd):
    if len(stack) < size:
        raise Exception(f"The command {cmd} wanted a stack with at least {size} items, but it had {len(stack)} items.")

async def run(prog, stack, output, stdout):
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
                run(stack.pop(), stack, output, stdout)
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
                
                # This list mess is what makes the interpreter print on newline.
                # output is essentially [["unflushed output here"]]
                # The reason it's doubly nested is so it can be modified when passed as an argument when recursing.
                
                # Append the string to print.
                output[0][0] += stack.pop()
                
                # Split by newline to know where to flush.
                output[0] = output[0][0].split("\n")
                
                # For all lines but the last, which are the ones ending with newline.
                for line in output[0][:-1]:
                    # Print and flush those lines.
                    await stdout.write(line)
                    await stdout.flush()
                
                # Delete the flushed lines.
                output[0] = [output[0][-1]]
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