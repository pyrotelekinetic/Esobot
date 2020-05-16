import aiohttp
import romkan
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
        jlpt = ", JLPT " + max(x.partition("-")[2] for x in entry_jlpt) if (entry_jlpt := entry["jlpt"]) else ""
        e = discord.Embed(
            title = f"Result #{menu.current_page + 1} ({'un' * (not entry['is_common'])}common{jlpt})",
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

    @commands.command(aliases=["hg", "kk", "ro"])
    async def romkan(self, ctx, *, text: commands.clean_content):
        """Convert romaji into hiragana or katakana, or vice-versa."""
        if text[:3] in ["hg ", "kk ", "ro "]:
            tp, text = text[:2], text[3:]
        else:
            tp = ctx.invoked_with
            if tp == "romkan":
                return await ctx.send("Please either use `!hg`, `!kk` or `!ro` (for hiragana, katakana and romaji respectively), or pass the type as an argument: `!romkan hg LyricLy wa baka desu yo`")
        if tp == "hg":
            await ctx.send(romkan.to_hiragana(text))
        elif tp == "kk":
            await ctx.send(romkan.to_katakana(text))
        elif tp == "ro":
            await ctx.send(romkan.to_hepburn(text))

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
