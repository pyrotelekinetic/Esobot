import aiohttp
import asyncio
import importlib
import os
import io

from discord.ext import commands
from urllib import parse
from constants import colors, info
from utils import make_embed


TIMEOUT = 60

def clean(text):
    return text.replace("```", "<triple backtick removed>")

def format_language(module_name):
    module = importlib.import_module(f"languages.{module_name.rsplit('.', 1)[0]}")
    return f"\N{BULLET} {module.display_name}\n```\n{clean(module.hello_world)}\n```"


class DiscordInput:
    def __init__(self, ctx):
        self.ctx = ctx
        self.buffer = ""

    async def read(self, amount):
        response = []
        for _ in range(amount):
            if not self.buffer:
                def check(message):
                    return (message.channel == self.ctx.channel and
                            message.author != self.ctx.bot.user and
                            message.author == self.ctx.author)
                message = await self.ctx.bot.wait_for("message", check=check)
                self.buffer = message.content + "\n"

            response.append(self.buffer[0])
            self.buffer = self.buffer[1:]
        return "".join(response)

    async def readline(self):
        result = ""
        while result[-1] != "\n":
            result.append(self.read(1))
        return result


class DiscordOutput:
    def __init__(self, message):
        self.message = message
        self.output = ""

    async def write(self, text):
        self.output += text
        if text.endswith("\n"):
            await self.flush()

    async def flush(self):
        await self.message.edit(content="```\n" + clean(self.output) + "\n```")


class Esolangs:
    """Commands related to esoteric programming languages."""

    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, 'session'):
            bot.session = aiohttp.ClientSession(loop=bot.loop, headers={"User-Agent": info.NAME})

    @commands.command(
        aliases=["ew", "w", "wiki"]
    )
    async def esowiki(self, ctx, *, esolang_name):
        """Link to the Esolang Wiki page for an esoteric programming language."""
        url = f"https://esolangs.org/wiki/{parse.quote(esolang_name)}"
        # npr = network path reference (https://stackoverflow.com/a/4978266/4958484)
        npr = f"//esolangs.org/wiki/{parse.quote(esolang_name.replace(' ', '_'))}"
        async with ctx.typing():
            async with ctx.bot.session.get('http:' + npr) as response:
                if response.status == 200:
                    await ctx.send('https:' + npr)
                else:
                    await ctx.send(embed=make_embed(
                        color=colors.EMBED_ERROR,
                        title="Error",
                        description=f"**{esolang_name.capitalize()}** is not on the Esolangs wiki. Make sure the capitalization is correct."
                    ))

    @commands.group(
        aliases=["run", "exe", "execute"],
        invoke_without_command=True
    )
    async def interpret(self, ctx, language, *, flags=""):
        """Interpret a program in an esoteric programming language."""
        try:
            interpreter = importlib.import_module(f"languages.{language.lower()}")
        except ImportError:
            await ctx.send(embed=make_embed(
                color=colors.EMBED_ERROR,
                title="Error",
                description=f"**{esolang_name}** has no interpreter at this point in time. Consider sending a pull request to add an interpreter."
            ))

        await ctx.send("Enter a program as a message or an attachment, or enter `@hello world` for a Hello World example.")
        def check(message):
            return (message.channel == ctx.channel and
                   (message.content or message.attachments) and
                    message.author == ctx.author)
        program_msg = await self.bot.wait_for("message", check=check)
        if program_msg.attachments:
            string = io.StringIO()
            program_msg.save(string)
            program = string.read()
        else:
            program = program_msg.content

        console = await ctx.send("```\n```")
        try:
            await asyncio.wait_for(
                interpreter.interpret(
                    program, 
                    flags, 
                    DiscordInput(ctx), 
                    DiscordOutput(console)
                ),
                TIMEOUT
            )
        except asyncio.TimeoutError:
            await console.edit(
                embed=make_embed(
                    title="Timeout", 
                    description=f"Execution timed out after {TIMEOUT} seconds."
                )
            )

    @interpret.command()
    async def list(self, ctx):
        """Get a list of languages supported currently."""
        await ctx.send(
            embed=make_embed(
                title="Languages",
                description="\n\n".join(format_language(x) for x in os.listdir("languages") if "__" not in x)
            )
        )


def setup(bot):
    bot.add_cog(Esolangs(bot))
