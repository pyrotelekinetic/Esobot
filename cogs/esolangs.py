import aiohttp
import asyncio
import importlib
import os
import io
import socket

from discord.ext import commands
from urllib import parse
from constants import colors, info
from utils import make_embed, clean


TIMEOUT = 60


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
                    return (
                        message.channel == self.ctx.channel
                        and message.author != self.ctx.bot.user
                        and message.author == self.ctx.author
                    )

                message = await self.ctx.bot.wait_for("message", check=check)
                self.buffer = message.content + "\n"

            response.append(self.buffer[0])
            self.buffer = self.buffer[1:]
        return "".join(response)

    async def readline(self):
        result = []
        while result[-1] != "\n":
            result.append(await self.read(1))
        return "".join(result)


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


class Esolangs(commands.Cog):
    """Commands related to esoteric programming languages."""

    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, "session"):
            bot.session = aiohttp.ClientSession(loop=bot.loop, headers={"User-Agent": info.NAME}, connector=aiohttp.TCPConnector(family=socket.AF_INET))

    @commands.command(aliases=["ew", "w", "wiki"])
    async def esowiki(self, ctx, *, esolang_name):
        """Link to the Esolang Wiki page for an esoteric programming language."""
        async with ctx.typing():
            print("doing")
            async with self.bot.session.get(
                "http://esolangs.org/w/api.php",
                params = {
                    "action": "opensearch",
                    "search": parse.quote(esolang_name)
                }
            ) as resp:
                print("returned")
                data = await resp.json()
        if not data[1]:
            return await ctx.send(
                embed=make_embed(
                    color=colors.EMBED_ERROR,
                    title="Error",
                    description=f"**{esolang_name.capitalize()}** wasn't found on the Esolangs wiki.",
                )
            )
        await ctx.send(data[3][0])

    @commands.group(aliases=["run", "exe", "execute"], invoke_without_command=True)
    async def interpret(self, ctx, language, *, flags=""):
        """Interpret a program in an esoteric programming language."""
        try:
            interpreter = importlib.import_module(f"languages.{language.lower()}")
        except ImportError:
            await ctx.send(
                embed=make_embed(
                    color=colors.EMBED_ERROR,
                    title="Error",
                    description=f"**{language}** has no interpreter at this point in time. Consider sending a pull request to add an interpreter.",
                )
            )
            return

        await ctx.send("Enter a program as a message or an attachment.")

        def check(message):
            return (
                message.channel == ctx.channel
                and (message.content or message.attachments)
                and message.author == ctx.author
            )

        program_msg = await self.bot.wait_for("message", check=check)
        if program_msg.attachments:
            string = io.StringIO()
            await program_msg.attachments[0].save(string)
            program = string.read()
        else:
            program = program_msg.content

        console = await ctx.send("```\n```")
        stdout = DiscordOutput(console)
        try:
            await asyncio.wait_for(interpreter.interpret(program, flags, DiscordInput(ctx), stdout),
                                   TIMEOUT)
            await stdout.flush()
        except asyncio.TimeoutError:
            await console.edit(
                embed=make_embed(
                    title="Timeout",
                    description=f"Execution timed out after {TIMEOUT} seconds.",
                )
            )

    @interpret.command()
    async def list(self, ctx):
        """Get a list of languages supported currently."""
        await ctx.send(
            embed=make_embed(
                title="Languages",
                description="\n\n".join(
                    format_language(x) for x in os.listdir("languages") if "__" not in x
                ),
            )
        )


def setup(bot):
    bot.add_cog(Esolangs(bot))
