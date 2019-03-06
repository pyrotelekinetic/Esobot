import asyncio

display_name = "DF (Deadfish)"
hello_world = """iisiiiisiiiiiiiioiiiiiiiiiiiiiiiiiiiiiiiiiiiiioiiiiiiiooiiio
dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddo
dddddddddddddddddddddsddoddddddddoiiioddddddoddddddddo"""


async def interpret(program, _, __, stdout):
	output = []
	i = 0
	for cmd in program:
		if i == -1 or i == 256:
			i = 0
		if cmd == "i":
			i += 1
		elif cmd == "d":
			i -= 1
		elif cmd == "s":
			i *= i
		elif cmd == "o":
			output.append(i)
	await stdout.write(" ".join(list(map(str, output))))
	await stdout.flush()