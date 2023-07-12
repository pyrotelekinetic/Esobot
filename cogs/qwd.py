import re
import math
import asyncio
from io import BytesIO
from collections import defaultdict

import discord
from PIL import Image, ImageDraw
from discord.ext import commands

from utils import save_json, load_json, get_pronouns
from constants.paths import QWD_SAVES


def parse_height(s):
    nums = re.findall(r"\d+(?:\.\d+)?", s)
    match [float(x) if "." in x else int(x) for x in nums]:
        case [cm]:
            return cm
        case [feet, inches]:
            return int(2.54 * (feet*12 + inches))
        case [feet, in_top, in_bottom]: 
            return int(2.54 * (feet*12 + in_top/in_bottom))
        case [feet, in_whole, in_top, in_bottom]:
            return int(2.54 * (feet*12 + in_whole + in_top/in_bottom))
        case _:
            raise commands.BadArgument("couldn't parse height")

def show_height(cm):
    base_in = math.ceil(cm / 2.54)
    feet, inches = divmod(base_in, 12)
    return f"{cm:.{int(isinstance(cm, float))}f}cm ({feet}'{inches}\")"

def rank_enumerate(xs, *, key):
    cur_idx = None
    cur_key = None
    for idx, x in enumerate(sorted(xs, key=key), start=1):
        if cur_key is None or key(x) >= cur_key:
            cur_idx = idx
            cur_key = key(x)
        yield (cur_idx, x)

def render_height_graph(height_member):
    # Dimensions: len*60 + 60 x 360
    # Margins: 30 x 20
    height_member.sort(key=lambda x: -x[0])
    base = Image.new('RGBA', (len(height_member * 60) + 60, 360), (200, 200, 200))
    max_height, min_height = height_member[0][0], height_member[-1][0]
    height_dif = max_height - min_height

    for i, (height, member, avatar) in enumerate(height_member):
        bar_height = math.ceil((height - min_height) * 280 / height_dif) + 20
        avatar = Image.open(BytesIO(avatar)).resize((60, bar_height))
        base.paste(avatar, (60 * i + 30, 340 - bar_height))

    draw = ImageDraw.Draw(base)
    draw.line([(30, 20), (30, 340), (len(height_member) * 60 + 30, 340)], (0, 0, 0), 1)
    # TODO: labels, title, etc.
    rendered = BytesIO()
    base.save(rendered, format='png')
    rendered.seek(0)
    return rendered


class Qwd(commands.Cog, name="QWD"):
    """Commands for QWD."""

    def __init__(self, bot):
        self.bot = bot
        self.qwdies = defaultdict(dict, load_json(QWD_SAVES))

    def cog_check(self, ctx):
        qwd = self.bot.get_guild(1047299292492206101)
        if ctx.guild != qwd and (ctx.guild or not qwd.get_member(ctx.author.id)):
            raise commands.CommandNotFound()
        return True

    @commands.group(invoke_without_command=True, aliases=["doxx"])
    @commands.guild_only()
    async def dox(self, ctx, *, target: discord.Member):
        """Reveal someone's address if they have set it through the bot. Must be used in a guild; the answer will be DMed to you."""
        p = get_pronouns(target)
        if not (addr := self.qwdies[str(target.id)].get("address")):
            return await ctx.send(f'{p.Subj()} {p.plrnt("do", "es")} have an address set.')
        await ctx.author.send(addr)
        await ctx.send(f"Alright, I've DMed you {p.pos_det} address.")

    @dox.command(name="set")
    @commands.dm_only()
    async def set_dox(self, ctx, *, address=""):
        """Set your address to be doxxed by others. Must be used in a DM with the bot. You can clear your address by using `set` without an argument."""
        self.qwdies[str(ctx.author.id)]["address"] = address
        save_json(QWD_SAVES, self.qwdies)
        if not address:
            await ctx.send("Successfully cleared your address.")
        else:
            await ctx.send("Successfully set your address.")     

    @commands.group(invoke_without_command=True)
    async def height(self, ctx, *, person: discord.Member = None):
        """Show someone's height if they have set it through the bot."""
        target = person or ctx.author
        p = get_pronouns(target)
        if not (height := self.qwdies[str(target.id)].get("height")):
            return await ctx.send(f'{p.Subj()} {p.plrnt("do", "es")} have a height set.')
        they_are = p.are() if person else "You're"
        await ctx.send(f"{they_are} {show_height(height)} tall.")

    @height.command(aliases=["lb", "top", "list"])
    async def leaderboard(self, ctx):
        """Show a ranking of people's heights."""
        people = []
        for k, v in self.qwdies.items():
            height = v.get("height")
            member = ctx.guild.get_member(int(k))
            if not height or not member or "razetime" in (member.global_name, member.name):
                continue
            people.append((height, member))

        entries = []
        for i, (height, member) in rank_enumerate(people, key=lambda x: x[0]):
            entries.append(rf"{i}\. {member.global_name or member.name} - {show_height(height)}")
        embed = discord.Embed(title="The shortest qwdies", colour=discord.Colour(0x75ffe3), description="\n".join(entries))
        await ctx.send(embed=embed)

    @height.command(name="set")
    async def set_height(self, ctx, *, height: parse_height):
        """Set your height (in cm or ft/in) for the height leaderboard. You can clear your height by passing `0`."""
        if height < 50:
            try:
                del self.qwdies[str(ctx.author.id)]["height"]
            except KeyError:
                await ctx.send("Did nothing.")
            else:
                await ctx.send("Successfully cleared your height.")
        else:
            self.qwdies[str(ctx.author.id)]["height"] = height
            await ctx.send(f"I set your height to {show_height(height)}.")
        save_json(QWD_SAVES, self.qwdies)

    @height.command()
    async def graph(self, ctx):
        """Graph a ranking of people's heights."""
        people = []
        for k, v in self.qwdies.items():
            height = v.get("height")
            member = ctx.guild.get_member(int(k))
            if not height or not member or "razetime" in (member.global_name, member.name):
                continue
            avatar = await member.avatar.read()
            people.append((height, member, avatar))

        image = await asyncio.to_thread(render_height_graph, people)
        await ctx.send(file=discord.File(image, filename='height_graph.png'))

async def setup(bot):
    await bot.add_cog(Qwd(bot))
