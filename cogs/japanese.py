import aiohttp
import asyncio
import pykakasi
import discord
import asyncio
import random

from googletrans import Translator

from utils import show_error
from discord.ext import commands, menus


def _translate(text):
    return Translator().translate(text, src="ja", dest="en").text

def format_jp_entry(entry):
    try:
        return f"{entry['word']}【{entry['reading']}】"
    except KeyError:
        try:
            return entry["reading"]
        except KeyError:
            try:
                return entry["word"]
            except KeyError:
                return "???"

class DictSource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=1)

    async def format_page(self, menu, entry):
        jlpt = ["JLPT " + max(x.partition("-")[2] for x in entry_jlpt)] if (entry_jlpt := entry["jlpt"]) else []
        common = ["common"] if "is_common" in entry and entry["is_common"] else []

        e = discord.Embed(
            title = f"Result #{menu.current_page + 1}",
            description = format_jp_entry(entry['japanese'][0])
        )
        if common or jlpt:
            title += " {', '.join(common + jlpt)})"
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

    @commands.command(aliases=["jp", "jsh", "dictionary", "dict"])
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

    @commands.command(aliases=["jatrans", "transja", "jtrans", "jptrans", "transjp", "transj", "tj", "jtr", "jpt", "jt",
                               "whatdidlyricjustsay", "what'dlyricsay", "whtdlysay", "wdls", "wls", "what",
                               "weebtrans", "weebt", "deweeb", "unweeb", "transweeb", "tweeb", "tw"])
    async def jatranslate(self, ctx, *, lyric_quote: commands.clean_content):
        t = await self.bot.loop.run_in_executor(None, _translate, lyric_quote)
        await ctx.send(t)

    @commands.command()
    @commands.guild_only()
    async def kanarace(self, ctx, kana: int = 10):
        """Race kana typing speeds!"""
        if not 1 <= kana <= 50:
            return await ctx.send("Use between 1 and 50 kana.")

        await ctx.send("Kana reading/typing race begins in 5 seconds. Get ready!")
        await asyncio.sleep(5)

        k = "あいうえおかきくけこがぎぐげごさしすせそざじずぜぞたちつてとだぢづでどなにぬねのはひふへほばびぶべぼぱぴぷぺぽまみむめもやゆよらりるれろわを"
        prompt = "".join(random.choices(k, k=kana))

        zwsp = "\u200b"
        start = await ctx.send(zwsp.join(prompt))
        winners = {}
        is_ended = asyncio.Event()
        timeout = False
        while not is_ended.is_set():
            done, pending = await asyncio.wait([
                self.bot.wait_for("message", check=lambda m: m.channel == ctx.channel and m.content == prompt and not m.author.bot and m.author not in winners),
                is_ended.wait()
            ], return_when=asyncio.FIRST_COMPLETED); [*map(asyncio.Task.cancel, pending)]
            r = done.pop().result()
            if isinstance(r, discord.Message):
                msg = r
            else:
                break
            await msg.delete()
            winners[msg.author] = (msg.created_at - start.created_at).total_seconds()
            if not timeout:
                timeout = True
                async def ender():
                    await asyncio.sleep(10)
                    is_ended.set()
                await ctx.send(f"{msg.author.name.replace('@', '@' + zwsp)} wins. Other participants have 10 seconds to finish.")
                self.bot.loop.create_task(ender())
        await ctx.send("\n".join(f"{i + 1}. {u.name.replace('@', '@' + zwsp)} - {t:.4f} seconds ({len(prompt) / t * 12:.2f}WPM)" for i, (u, t) in enumerate(winners.items())))


def setup(bot):
    bot.add_cog(Japanese(bot))
