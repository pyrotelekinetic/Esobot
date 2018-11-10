import json

display_name = "WHY (would you ever want this)"
hello_world = """#include <stdio.h>
printf("Hello, World\n");
return 0;"""

# Non-JIT-mode WHY compiler
def build_C(code, mx):
        thing = f"""
#define QUITELONG long long int
const QUITELONG max = {mx};

int main() {{
        volatile QUITELONG i = 0; // disable some "optimizations" that RUIN OUR BEAUTIFUL CODE!
        while (i < max) {{
                i++;
        }}
        {code}
}}
        """
        return thing


def compile(contents):
    return build_C(
        contents,
        1000000000
    )

async def interpret(program, _, stdin, stdout):
	ctx = stdin.ctx # The Esobot interpreter handling is weird...

	data = {
		"cmd": "gcc -x c main.cpp && ./a.out",
		"src": compile(program)
	}

	# okay, yes, mostly copied from https://github.com/Rapptz/RoboDanny/blob/f6638d520ea0f559cb2ae28b862c733e1f165970/cogs/lounge.py
	async with ctx.session.post('http://coliru.stacked-crooked.com/compile', data=data) as resp:
		if resp.status != 200:
			await stdout.write('Coliru did not respond in time.')
			return

		output = await resp.text(encoding='utf-8')

		if len(output) < 1992:
			await stdout.write(f'```\n{output}\n```')
			return

		# output is too big so post it in gist
		async with ctx.session.post('http://coliru.stacked-crooked.com/share', data=data) as r:
			if r.status != 200:
				await stdout.write('Could not create coliru shared link')
			else:
				shared_id = await r.text()
				await stdout.write(f'Output too big. Coliru link: http://coliru.stacked-crooked.com/a/{shared_id}')