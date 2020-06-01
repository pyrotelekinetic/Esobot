import aiohttp
import pykakasi
import discord
from utils import show_error
from discord.ext import commands, menus


def format_jp_entry(entry):
    try:
        return f"{entry['word']}【{entry['reading']}】"
    except KeyError:
        return entry["reading"]

class DictSource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=1)

    async def format_page(self, menu, entry):
        jlpt = ["JLPT " + max(x.partition("-")[2] for x in entry_jlpt)] if entry_jlpt := entry["jlpt"] else []
        try:
            common = ["{'un' * (not entry['is_common']}common"]
        except KeyError:
            common = []
        e = discord.Embed(
            title = f"Result #{menu.current_page + 1} (', '.join(common + jlpt))",
            description = format_jp_entry(entry['japanese'][0])
        )
        for i, sense in enumerate(entry["senses"], start=1):
            e.add_field(
                name = ", ".join(sense["parts_of_speech"]) if sense["parts_of_speech"] else "\u200b",
                value = " | ".join(
                    [f"{i}. " + "; ".join(sense["english_definitions"])] +
                    [tags := ", ".join(f"*{x}*" for x in sense["tags"] + sense["info"])] * bool(tags)
                ),
                inline=False
            )
        if len(entry["japanese"]) > 1:
            e.add_field(name = "Other forms", value = "\n".join(format_jp_entry(x) for x in entry["japanese"][1:]), inline=False)
        return e

class Japanese(commands.Cog):
    """Weeb stuff."""

    def __init__(self, bot):
        self.bot = bot
        kakasi = pykakasi.kakasi()
        kakasi.setMode("H", "a")
        kakasi.setMode("K", "a")
        kakasi.setMode("J", "a")
        kakasi.setMode("s", True)
        self.conv = kakasi.getConverter()

    @commands.command(aliases=["ro", "roman", "romanize", "romanise"])
    async def romaji(self, ctx, *, text: commands.clean_content):
        """Romanize Japanese text."""
        await ctx.send(self.conv.do(text))

    @commands.command(aliases=["jp", "jsh"])
    async def jisho(self, ctx, *, query):
        """Look things up in the Jisho dictionary."""
        async with self.bot.session.get("https://jisho.org/api/v1/search/words", params={"keyword": query}) as resp:
            if resp.status == 200:
                data = await resp.json()
            else:
                data = None
        if not data["data"]:
            return await show_error(ctx, "That query returned no results.")
        pages = menus.MenuPages(source=DictSource(data["data"]), clear_reactions_after=True)
        await pages.start(ctx)

def setup(bot):
    bot.add_cog(Japanese(bot))
