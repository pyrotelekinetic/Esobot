import asyncio
import datetime
import io
import os
import random
import uuid
import shlex
from textwrap import dedent
from typing import Optional

import discord
from discord.ext import commands, tasks
from PIL import Image, ImageOps

from constants.paths import ADDRESS_SAVES
from utils import aggressive_normalize, load_json, save_json


@commands.check
def is_in_esolangs(ctx):
    if ctx.guild.id != 346530916832903169:
        raise commands.CommandNotFound()
    return True

@commands.check
def is_olivia(ctx):
    if ctx.author.id not in (156021301654454272, 319753218592866315):
        raise commands.CommandNotFound()
    return True


class Temporary(commands.Cog):
    """Temporary, seasonal, random and miscellaneous poorly-written functionality. Things in here should probably be developed further or removed at some point."""

    def __init__(self, bot):
        self.bot = bot
        self.last_10 = None
        self.addresses = load_json(ADDRESS_SAVES)
        #self.pride_loop.start()

    # 1AM UTC
    @tasks.loop(
        time=datetime.time(1),
    )
    async def pride_loop(self):
        PATH = "./assets/limes/"
        l = sorted(os.listdir(PATH))
        if "index" in l:
            with open(PATH + "index") as f:
                i = int(f.read())
        else:
            random.shuffle(l)
            for i, f in enumerate(l):
                name = f"{i:0>{len(str(len(l)))}}-{uuid.uuid4()}"
                os.replace(PATH + f, PATH + name)
                l[i] = name
            i = 0
        next_lime = l[i]
        i += 1
        if i >= len(l)-1:
            os.remove(PATH + "index")
        else:
            with open(PATH + "index", "w") as f:
                f.write(str(i))
        with open(PATH + next_lime, "rb") as f:
            d = f.read()
        await self.bot.get_guild(346530916832903169).edit(icon=d)

    @pride_loop.before_loop
    async def before_pride_loop(self):
        await self.bot.wait_until_ready()

    # def get_members(self, channel, *, excluding=None):
    #     if channel.category.id != 730233425251794983:
    #         return None
    #     l = [m for m in channel.members if not any(r.name in ("Administrators", "Esobot") for r in m.roles) and m != excluding]
    #     return l if 1 <= len(l) <= 2 else None

    # @commands.command()
    # async def start(self, ctx):
    #     try:
    #         partner = self.get_members(ctx.channel, excluding=ctx.author)[0]
    #     except TypeError:
    #         return await ctx.send("You're not in a game channel.")
    #     await ctx.send(f"Beginning a start request. Your partner, {partner}, must agree to begin the event in 30 seconds by typing `!accept`!")
    #     try:
    #         await self.bot.wait_for("message", check=lambda m: m.channel == ctx.channel and m.content == "!accept", timeout=30)
    #     except asyncio.TimeoutError:
    #         await ctx.send("Request not accepted.")
    #     else:
    #         await ctx.send("Let the games begin!")
    #         playing = ctx.guild.get_role(730594078584078378)
    #         await ctx.author.add_roles(playing)
    #         await partner.add_roles(playing)
    #         await self.bot.get_channel(730593893195710525).send(f"Game started in {ctx.channel.mention}.")

    # @commands.command()
    # async def submit(self, ctx, *, text: commands.clean_content = ""):
    #     """Submit your submission for the event. Accepts a text argument, which should be a URL or similar to your solution. Sends everything to a logging channel to be verified."""
    #     try:
    #         partner = self.get_members(ctx.channel, excluding=ctx.author)[0]
    #     except TypeError:
    #         return await ctx.send("You're not in a game channel.")
    #     playing = ctx.guild.get_role(730594078584078378)
    #     if playing not in ctx.author.roles or playing not in partner.roles:
    #         await ctx.send("You have to be playing to submit.")
    #     await ctx.send("Ending the game. Look over this and make absolutely certain that it is correct! You can't take back your submission! Your partner must agree to submit in 60 seconds by typing `!accept`.")
    #     try:
    #         await self.bot.wait_for("message", check=lambda m: m.channel == ctx.channel and m.content == "!accept", timeout=60)
    #     except asyncio.TimeoutError:
    #         await ctx.send("Request not accepted.")
    #     else:
    #         await ctx.author.remove_roles(playing)
    #         await partner.remove_roles(playing)
    #         await self.bot.get_channel(730593893195710525).send(f"{ctx.channel.mention} finished with the following submission: {text}")

    @commands.command()
    async def identicon(self, ctx, username: str, color: Optional[discord.Colour] = discord.Colour(0xF0F0F0), alpha: float = 0.0):
        """Send someone's GitHub identicon. `color` and `alpha` control the background colour."""

        if not 0 <= alpha <= 1.0:
            return await ctx.send("`alpha` must be between 0 and 1.")
        colour = (*color.to_rgb(), int(255*alpha))

        async with self.bot.session.get(f"https://github.com/identicons/{username}.png") as resp:
            if resp.status != 200:
                return await ctx.send("404ed trying to access that identicon.")
            b = io.BytesIO(await resp.read())

        i = Image.open(b, formats=["png"]).convert("RGBA")

        # this sucks
        default = (0xF0, 0xF0, 0xF0, 0xFF)
        w, h = i.size
        if colour != default:
            data = i.load()
            for y in range(h):
                for x in range(w):
                    if data[x, y] == default:
                        data[x, y] = colour

        i2 = Image.new("RGBA", (512, 512), colour)
        i2.paste(i, ((512-w)//2, (512-h)//2))

        b.seek(0)
        i2.save(b, "png")
        b.truncate()
        b.seek(0)
        await ctx.send(file=discord.File(b, "result.png"))

    @commands.group(hidden=True, invoke_without_command=True, aliases=["doxx"])
    @commands.guild_only()
    async def dox(self, ctx, *, target: discord.Member):
        """Reveal someone's address if they have set it through the bot. Must be used in a guild; the answer will be DMed to you."""
        if not (addr := self.addresses.get(str(target.id))):
            return await ctx.send("That user doesn't have an address set.")
        await ctx.author.send(addr)
        await ctx.send("Alright, I've DMed you their address.")
        

    @dox.group(hidden=True)
    @commands.dm_only()
    async def set(self, ctx, *, address=""):
        """Set your address to be doxxed by others. Must be used in a DM with the bot. You can clear your address by using `set` without an argument."""
        self.addresses[str(ctx.author.id)] = address
        save_json(ADDRESS_SAVES, self.addresses)
        if not address:
            await ctx.send("Successfully cleared your address.")
        else:
            await ctx.send("Successfully set your address.")

    @commands.group(hidden=True, invoke_without_command=True)
    async def olivia(self, ctx):
        pass

    @olivia.command(name="time", hidden=True)
    @is_in_esolangs
    async def _time(self, ctx):
        await self.bot.get_command("time")(ctx, user=ctx.guild.get_member(156021301654454272))

    @commands.group(hidden=True, invoke_without_command=True, aliases=["ky", "kay", "k"])
    async def kaylynn(self, ctx):
        pass

    @kaylynn.command(name="time", hidden=True)
    @is_in_esolangs
    async def _time2(self, ctx):
        await self.bot.get_command("time")(ctx, user=ctx.guild.get_member(636797375184240640))

    @kaylynn.command(hidden=True)
    async def cute(self, ctx):
        if ctx.guild.id == 346530916832903169:
            await ctx.send("yeah!")

    @commands.group(hidden=True, invoke_without_command=True)
    async def soup(self, ctx):
        pass

    @soup.command(name="time", hidden=True)
    @is_in_esolangs
    @is_olivia
    async def _time3(self, ctx):
        await ctx.send("<@636797375184240640> <@309787486278909952> <@319753218592866315> <@224379582785126401> <@166910808305958914> <@275982450432147456> soup time !!")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user and len(message.content.split(" ")) == 10:
            self.last_10 = message.created_at
        if self.last_10 and message.author.id == 509849474647064576 and len(message.content.split(" ")) == 10 and (message.created_at - self.last_10).total_seconds() < 1.0:
            await message.delete()

        if message.author.id == 319753218592866315 and message.content.count("night") >= 10:
            msg = ""
            c = 0
            for idx, word in enumerate(message.content.split(), start=1):
                if word == "night":
                    c += 1
                else:
                    msg += f"Word {idx} is misspelled: ``{word}``\n"
            msg += f"That's {c}."
            await message.channel.send(msg)


def setup(bot):
    bot.add_cog(Temporary(bot))
