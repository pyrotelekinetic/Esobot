import asyncio
import datetime
import dateparser
import discord
import json
import pytz
import time
import itertools

from constants import colors, channels, paths
from collections import namedtuple
from discord.ext import commands
from utils import make_embed, clean


Event = namedtuple("Event", ["name", "times", "members"])


class Time:
    """Commands related to time and delaying messages."""

    def __init__(self, bot):
        self.bot = bot
        with open(paths.CONFIG_FOLDER + "/" + paths.TIME_SAVES) as f:
            self.time_config = json.load(f)
        with open(paths.CONFIG_FOLDER + "/" + paths.EVENT_SAVES) as f:
            self.event_config = {}
            save = json.load(f)
            for event in save:
                self.event_config[event] = Event(*save[event])

    def get_time(self, timezone_name):
        timezone = pytz.timezone(timezone_name)
        now = datetime.datetime.now().astimezone(timezone)
        return now.strftime("**%H:%M** (**%I:%M%p**) on %A (%Z, UTC%z)")

    @commands.group(
        aliases=["tz", "when", "t"],
        invoke_without_command=True
    )
    async def time(self, ctx, *, user: discord.Member = None):
        """Get a user's time."""
        user = ctx.author if not user else user
        try:
            time = self.get_time(self.time_config[str(user.id)])
        except KeyError:
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
        else:
            await ctx.send(
                embed=make_embed(
                    title=f"{user.name}'s time",
                    description=time,
                    color=colors.EMBED_SUCCESS
                )
            )

    @time.command()
    async def set(self, ctx, timezone="invalid"):
        """Set a timezone for you in the database."""
        try:
            pytz.timezone(timezone)
            self.time_config[str(ctx.author.id)] = timezone
            await self.update_times()
            with open(paths.CONFIG_FOLDER + "/" + paths.TIME_SAVES, "w") as f:
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
        """Remove your timezone from the database."""
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
        await self.update_times()
        with open(paths.CONFIG_FOLDER + "/" + paths.TIME_SAVES, "w") as f:
            json.dump(self.time_config, f)

        await ctx.send(
            embed=make_embed(
                title="Unset timezone",
                description=f"Your timezone is now unset.",
                color=colors.EMBED_SUCCESS
            )
        )

    async def time_loop(self):
        while True:
            await self.bot.wait_until_ready()

            while True:
                if int(time.time()) % 60 == 0:
                    break
                await asyncio.sleep(0)

            while not self.bot.is_closed():
                await self.update_times()
                await asyncio.sleep(60)

    async def update_times(self):
        channel = self.bot.get_channel(channels.TIME_CHANNEL)
        await channel.purge()

        paginator = commands.Paginator()
        time_config_members = {channel.guild.get_member(int(id)): timezone 
                               for id, timezone in self.time_config.items()
                               if channel.guild.get_member(int(id))}
        groups = itertools.groupby(
            sorted(
                time_config_members.items(), 
                key=lambda m: (
                    datetime.datetime.now().astimezone(pytz.timezone(m[1])).replace(tzinfo=None).year,
                    datetime.datetime.now().astimezone(pytz.timezone(m[1])).replace(tzinfo=None).month,
                    datetime.datetime.now().astimezone(pytz.timezone(m[1])).replace(tzinfo=None).day,
                    self.get_time(m[1]),
                    str(m[0])
                )
            ),
            lambda x: self.get_time(x[1])
        )
        for key, group in groups:
            if not key:
                continue
            group_message = [key]
            for member, _ in group:
                group_message.append(member.mention)
            paginator.add_line("\n    ".join(group_message))

        for page in paginator.pages:
            await channel.send(embed=make_embed(title="Times", description=page[3:-3]))

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
        """Ping when the user is online."""
        message = f"{member.mention}, {ctx.author.mention} has sent you a scheduled ping." + (f" A message was attached:\n\n```\n{clean(message)}\n```" if message else "")
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
        """Ping when the user is not playing a game."""
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

    @commands.group(
        aliases=["ev", "feed"]
    )
    async def event(self, ctx):
        """Commands related to events."""

    @event.command()
    async def create(self, ctx, name, *, times=""):
        """Create an event.
        If no times are given, the event will only be able to be triggered manually.
        Otherwise, you can schedule triggers, like `3 hours later` or `12:30PM`, seperated by commas.
        If you have a time added with the `time` command, your timezone will be assumed. Otherwise, UTC will be used unless you specify a timezone like `at 12:30PM EST`.
        Example usage: `event create game in two minutes, 6PM`
        """
        if name.lower() in self.event_config:
            await ctx.send(
                embed=make_embed(
                    title="Error",
                    description="That event already exists.",
                    color=colors.EMBED_ERROR
                )
            )
            return
        event = Event(name, [], [])
        await self.parse_times(ctx, event, times)

        self.event_config[name.lower()] = event
        with open(paths.CONFIG_FOLDER + "/" + paths.EVENT_SAVES, "w") as f:
            saving = {}
            for event in self.event_config:
                saving[event] = list(self.event_config[event])
            json.dump(saving, f)
        await ctx.send(
            embed=make_embed(
                title="Added event",
                description="Your event was created successfully.",
                color=colors.EMBED_SUCCESS
            )
        )

    @event.command()
    async def remove(self, ctx, name):
        """Remove an event."""
        if name.lower() not in self.event_config:
            await ctx.send(
                embed=make_embed(
                    title="Error",
                    description="That event doesn't exist.",
                    color=colors.EMBED_ERROR
                )
            )
            return
        self.event_config.pop(name.lower())
        with open(paths.CONFIG_FOLDER + "/" + paths.EVENT_SAVES, "w") as f:
            saving = {}
            for event in self.event_config:
                saving[event] = list(self.event_config[event])
            json.dump(saving, f)
        await ctx.send(
            embed=make_embed(
                title="Deleted event",
                description="Your event was removed successfully.",
                color=colors.EMBED_SUCCESS
            )
        )

    @event.command()
    async def schedule(self, ctx, name, *, times):
        """Add more scheduled times to an existing event."""
        if name.lower() not in self.event_config:
            await ctx.send(
                embed=make_embed(
                    title="Error",
                    description="That event doesn't exist.",
                    color=colors.EMBED_ERROR
                )
            )
            return
        await self.parse_times(ctx, self.event_config[name.lower()], times)
        await ctx.send(
            embed=make_embed(
                title="Scheduled time",
                description="Successfully added a new scheduled time to that event.",
                color=colors.EMBED_ERROR
            )
        )

    @event.command()
    async def trigger(self, ctx, name, *, message=None):
        """Trigger an event manually."""
        await self.trigger_event(name.lower(), message)

    @event.command(
        aliases=["sub"]
    )
    async def subscribe(self, ctx, name):
        """Subscribe to an event."""
        if name.lower() not in self.event_config:
            await ctx.send(
                embed=make_embed(
                    title="Error",
                    description="That event doesn't exist.",
                    color=colors.EMBED_ERROR
                )
            )
            return
        if str(ctx.author.id) in self.event_config[name.lower()].members:
            await ctx.send(
                embed=make_embed(
                    title="Error",
                    description="You're already subscribed to that event.",
                    color=colors.EMBED_ERROR
                )
            )
            return
        self.event_config[name.lower()].members.append(str(ctx.author.id))
        with open(paths.CONFIG_FOLDER + "/" + paths.EVENT_SAVES, "w") as f:
            saving = {}
            for event in self.event_config:
                saving[event] = list(self.event_config[event])
            json.dump(saving, f)
        await ctx.send(
            embed=make_embed(
                title="Subscribed to event",
                description=("You were successfully subscribed to that event.\n"
                "Make sure that the bot is able to DM you, "
                "i.e. that you haven't blocked it and you have DMs from non-friends enabled on this server."),
                color=colors.EMBED_SUCCESS
            )
        )

    @event.command(
        aliases=["unsub"]
    )
    async def unsubscribe(self, ctx, name):
        """Unsubscribe to an event."""
        if name.lower() not in self.event_config:
            await ctx.send(
                embed=make_embed(
                    title="Error",
                    description="That event doesn't exist.",
                    color=colors.EMBED_ERROR
                )
            )
            return
        if str(ctx.author.id) not in self.event_config[name.lower()].members:
            await ctx.send(
                embed=make_embed(
                    title="Error",
                    description="You're not subscribed to that event.",
                    color=colors.EMBED_ERROR
                )
            )
            return
        self.event_config[name.lower()].members.remove(str(ctx.author.id))
        with open(paths.CONFIG_FOLDER + "/" + paths.EVENT_SAVES, "w") as f:
            saving = {}
            for event in self.event_config:
                saving[event] = list(self.event_config[event])
            json.dump(saving, f)
        await ctx.send(
            embed=make_embed(
                title="Unsubscribed to event",
                description="You were successfully unsubscribed to that event.",
                color=colors.EMBED_SUCCESS
            )
        )

    async def trigger_event(self, name, message=None):
        event = self.event_config[name]
        for id in event.members:
            user = self.bot.get_user(int(id))
            if not user:
                continue
            await user.send(
                embed=make_embed(
                    title=f"{event.name}",
                    description=message or f"This event has triggered."
                )
            )

    async def parse_times(self, ctx, event, times):
        for t in times.split(","):
            parsed = dateparser.parse(t.strip(), settings={"TIMEZONE": "UTC", "TO_TIMEZONE": "UTC"})
            print(parsed)
            if parsed:
                if not parsed.tzinfo and not parsed.microsecond and not str(ctx.author.id) in self.time_config:
                    parsed = parsed.replace(tzinfo=datetime.timezone.utc).astimezone(pytz.timezone(self.time_config[str(ctx.member.id)]))
                if parsed < datetime.datetime.utcnow():
                    await ctx.send("Timestamp is in the past. Try looking your times over; maybe you missed an 'in' or 'later'?")
                    continue
                event.times.append(time.mktime(parsed.timetuple()))
        event.times.sort()

    async def event_loop(self):
        await self.bot.wait_until_ready()
        while True:
            while not self.bot.is_closed():
                for event in self.event_config:
                    if self.event_config[event].times and time.time() >= self.event_config[event].times[0]:
                        self.event_config[event].times.pop(0)
                        with open(paths.CONFIG_FOLDER + "/" + paths.EVENT_SAVES, "w") as f:
                            saving = {}
                            for event in self.event_config:
                                saving[event] = list(self.event_config[event])
                            json.dump(saving, f)
                        await self.trigger_event(event)
                await asyncio.sleep(1)


def setup(bot):
    time = Time(bot)
    bot.loop.create_task(time.time_loop())
    bot.loop.create_task(time.event_loop())
    bot.add_cog(time)
