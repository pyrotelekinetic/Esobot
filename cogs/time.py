import asyncio
import discord
import json
import pytz
import time

from constants import colors, channels, paths
from utils import make_embed
from discord.ext import commands
from datetime import datetime


class Time:
    """Commands related to time and delaying messages."""

    def __init__(self, bot):
        self.bot = bot
        with open(paths.TIME_SAVES) as f:
            self.time_config = json.load(f)

    def get_time(self, id):
        if str(id) not in self.time_config:
            return None

        now = datetime.now(pytz.timezone(self.time_config[str(id)]))
        return now.strftime("%H:%M on %A, timezone %Z%z")

    @commands.group(
        aliases=["tz", "when", "t"],
        invoke_without_command=True
    )
    async def time(self, ctx, *, user: discord.Member = None):
        user = ctx.author if not user else user
        time = self.get_time(user.id)

        if not time:
            message = ("You don't have a timezone set. You can set one with `time set`." if user == ctx.author
                  else "That user doesn't have a timezone set.")
            await ctx.send(
                embed=make_embed(
                    title="Timezone not set",
                    description=message,
                    color=colors.EMBED_ERROR
                )
            )
            return

        await ctx.send(
            embed=make_embed(
                title=f"{user.name}'s time",
                description=time,
                color=colors.EMBED_SUCCESS
            )
        )

    @time.command()
    async def set(self, ctx, timezone="invalid"):
        try:
            pytz.timezone(timezone)
            self.time_config[str(ctx.author.id)] = timezone
            with open(paths.TIME_SAVES, "w") as f:
                json.dump(self.time_config, f)
            await ctx.send(
                embed=make_embed(
                    title="Set timezone",
                    description=f"Your timezone is now {timezone}.",
                    color=colors.EMBED_SUCCESS
                )
            )
        except pytz.exceptions.UnknownTimeZoneError:
            url = "https://github.com/sdispater/pytzdata/blob/master/pytzdata/_timezones.py"
            await ctx.send(
                embed=make_embed(
                    title="Invalid timezone",
                    description="You either set an invalid timezone or didn't specify one at all. "
                               f"Read a list of valid timezone names [here]({url}).",
                    color=colors.EMBED_ERROR
                )
            )

    @time.command(
        aliases=["remove"]
    )
    async def unset(self, ctx):
        if str(ctx.author.id) not in self.time_config:
            await ctx.send(
                embed=make_embed(
                    title="...I'm sorry?",
                    description=f"You don't have a timezone set.",
                    color=colors.EMBED_ERROR
                )
            )
            return
        self.time_config.pop(str(ctx.author.id))
        with open(paths.TIME_SAVES, "w") as f:
            json.dump(self.time_config, f)
        await ctx.send(
            embed=make_embed(
                title="Unset timezone",
                description=f"Your timezone is now unset.",
                color=colors.EMBED_SUCCESS
            )
        )

    async def time_loop(self, channel_id):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(channel_id)
        while True:
            if int(time.time()) % 60 == 0:
                break
            await asyncio.sleep(0)

        while True:
            await channel.purge()
            paginator = commands.Paginator()
            for id in self.time_config:
                member = discord.utils.get(channel.guild.members, id=int(id))
                # member may be None if the member left the server since putting their timezone in
                if member:
                    paginator.add_line(f"{member.mention}'s time is {self.get_time(id)}")
            for page in paginator.pages:
                await channel.send(embed=make_embed(title="Times", description=page[3:-3]))
            await asyncio.sleep(60)

    @commands.group(
        aliases=["pw", "pwhen", "pingw"]
    )
    async def pingwhen(self, ctx):
        """Ping someone when a certain criterium is met.
        If the condition does not complete after 48 hours, then the command will terminate.
        """

    @pingwhen.command(
        aliases=["on"]
    )
    async def online(self, ctx, member: discord.Member, *, message=None):
        message = f"{member.mention}, {ctx.author.mention} has sent you a scheduled ping." + (f" A message was attached:\n\n```\n{message}\n```" if message else "")
        await ctx.send(
            embed=make_embed(
                title="Ping scheduled",
                description=f"{member.mention} will be pinged when they go online with the message:\n\n{message}",
                color=colors.EMBED_SUCCESS
            )
        )
        if member.status != discord.Status.online:
            await self.bot.wait_for(
                "member_update", 
                check=lambda before, after: after.id == member.id and after.status == discord.Status.online
            )
        await ctx.send(message)

    @pingwhen.command(
        aliases=["nogame"]
    )
    async def free(self, ctx, member: discord.Member, *, message=None):
        message = f"{member.mention}, {ctx.author.mention} has sent you a scheduled ping." + (f" A message was attached:\n\n```\n{message}\n```" if message else "")
        await ctx.send(
            embed=make_embed(
                title="Ping scheduled",
                description=f"{member.mention} will be pinged when they stop playing a game with the message:\n\n{message}",
                color=colors.EMBED_SUCCESS
            )
        )
        if member.activity:
            await self.bot.wait_for(
                "member_update", 
                check=lambda before, after: after.id == member.id and after.activity == None
            )
        await ctx.send(message)


def setup(bot):
    time = Time(bot)
    bot.loop.create_task(time.time_loop(channels.TIME_CHANNEL))
    bot.add_cog(Time(bot))
