import aiohttp
import socket

from discord.ext import commands
from urllib import parse
from constants import colors, info
from utils import make_embed


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
            async with self.bot.session.get(
                "http://esolangs.org/w/api.php",
                params = {
                    "action": "opensearch",
                    "search": parse.quote(esolang_name)
                }
            ) as resp:
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


def setup(bot):
    bot.add_cog(Esolangs(bot))
