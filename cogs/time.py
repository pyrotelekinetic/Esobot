import asyncio
import calendar
import datetime
import dateparser
import discord
import json
import pytz
import time
import itertools

from constants import colors, channels, paths
from collections import namedtuple
from discord.ext import commands, tasks
from utils import make_embed, clean, show_error, load_json, save_json


class Event(commands.Converter):
    def __init__(self, name=None, times=None, members=None, owner=None, managers=None):
        self.name = name
        self.times = times
        self.members = members
        self.owner = owner
        self.managers = managers

    def __iter__(self):
        return iter([self.name, self.times, self.members, self.owner, self.managers])

    async def convert(self, ctx, argument):
        try:
            return event_config[argument.lower()]
        except KeyError:
            raise commands.BadArgument("That event doesn't exist.")


save = load_json(paths.EVENT_SAVES)
event_config = {}
for event in save:
    event_config[event] = Event(*save[event])


class Time(commands.Cog):
    """Commands related to time and delaying messages."""

    def __init__(self, bot):
        self.bot = bot
        self.time_config = load_json(paths.TIME_SAVES)
        self.time_loop.start()
        self.event_loop.start()

    def cog_unload(self):
        self.time_loop.cancel()
        self.event_loop.cancel()

    def get_time(self, timezone_name):
        timezone = pytz.timezone(timezone_name)
        now = datetime.datetime.now().astimezone(timezone)
        return now.strftime("**%H:%M** (**%I:%M%p**) on %A (%Z, UTC%z)")

    @commands.group(aliases=["tz", "when", "t"], invoke_without_command=True)
    async def time(self, ctx, *, user: discord.Member = None):
        """Get a user's time."""
        user = ctx.author if not user else user
        try:
            time = self.get_time(self.time_config[str(user.id)])
        except KeyError:
            message = (
                "You don't have a timezone set. You can set one with `time set`."
                if user == ctx.author
                else "That user doesn't have a timezone set."
            )
            await show_error(ctx, message, "Timezone not set")
        else:
            await ctx.send(
                embed=make_embed(
                    title=f"{user.name}'s time",
                    description=time,
                    color=colors.EMBED_SUCCESS,
                )
            )

    @time.command()
    async def set(self, ctx, timezone="invalid"):
        """Set a timezone for you in the database."""
        try:
            pytz.timezone(timezone)
            self.time_config[str(ctx.author.id)] = timezone
            await self.update_times()
            save_json(paths.TIME_SAVES, self.time_config)

            await ctx.send(
                embed=make_embed(
                    title="Set timezone",
                    description=f"Your timezone is now {timezone}.",
                    color=colors.EMBED_SUCCESS,
                )
            )
        except pytz.exceptions.UnknownTimeZoneError:
            url = "https://github.com/sdispater/pytzdata/blob/master/pytzdata/_timezones.py"
            await show_error(
                ctx,
                message="You either set an invalid timezone or didn't specify one at all. "
                f"Read a list of valid timezone names [here]({url}).",
                title="Invalid timezone",
            )

    @time.command(aliases=["remove"])
    async def unset(self, ctx):
        """Remove your timezone from the database."""
        if str(ctx.author.id) not in self.time_config:
            await show_error(ctx, "You don't have a timezone set.")

        self.time_config.pop(str(ctx.author.id))
        await self.update_times()
        save_json(paths.TIME_SAVES, self.time_config)

        await ctx.send(
            embed=make_embed(
                title="Unset timezone",
                description=f"Your timezone is now unset.",
                color=colors.EMBED_SUCCESS,
            )
        )

    async def update_times(self):
        paginator = commands.Paginator()
        time_config_members = {
            channel.guild.get_member(int(id)): timezone
            for id, timezone in self.time_config.items()
            if channel.guild.get_member(int(id))
        }
        groups = itertools.groupby(
            sorted(
                time_config_members.items(),
                key=lambda m: (
                    datetime.datetime.now()
                    .astimezone(pytz.timezone(m[1]))
                    .replace(tzinfo=None)
                    .year,
                    datetime.datetime.now()
                    .astimezone(pytz.timezone(m[1]))
                    .replace(tzinfo=None)
                    .month,
                    datetime.datetime.now()
                    .astimezone(pytz.timezone(m[1]))
                    .replace(tzinfo=None)
                    .day,
                    self.get_time(m[1]),
                    str(m[0]),
                ),
            ),
            lambda x: self.get_time(x[1]),
        )
        for key, group in groups:
            if not key:
                continue
            group_message = [key]
            for member, _ in group:
                group_message.append(member.mention)
            paginator.add_line("\n    ".join(group_message))
        
        # Get the bot's own messages in the channel
        channel = self.bot.get_channel(channels.TIME_CHANNEL)
        own_messages = await channel.history().flatten()
        
        # Delete extra ones
        if len(own_messages) > len(paginator.pages):
            await channel.purge(limit=len(own_messages) - len(paginator.pages))
        
        # Edit messages
        for i, page in enumerate(paginator.pages):
            try:
                await own_messages[i].edit(embed=make_embed(title="Times", description=page[3:-3]))
            except IndexError:
                await channel.send(embed=make_embed(title="Times", description=page[3:-3]))

    time_loop = tasks.loop(minutes=1)(update_times)

    @time_loop.before_loop
    async def before_time(self):
        await self.bot.wait_until_ready()

    @commands.group(aliases=["pw", "pwhen", "pingw"])
    async def pingwhen(self, ctx):
        """Ping someone when a certain criterium is met.
        If the condition does not complete after 48 hours, then the command will terminate.
        """

    @pingwhen.command(aliases=["on"])
    async def online(self, ctx, member: discord.Member, *, message=None):
        """Ping when the user is online."""
        message = (
            f"{member.mention}, {ctx.author.mention} has sent you a scheduled ping."
            + (
                f" A message was attached:\n\n```\n{clean(message)}\n```"
                if message
                else ""
            )
        )
        await ctx.send(
            embed=make_embed(
                title="Ping scheduled",
                description=f"{member.mention} will be pinged when they go online with the message:\n\n{message}",
                color=colors.EMBED_SUCCESS,
            )
        )
        if member.status != discord.Status.online:
            await self.bot.wait_for(
                "member_update",
                check=lambda before, after: after.id == member.id
                and after.status == discord.Status.online,
            )
        await ctx.send(message)

    @pingwhen.command(aliases=["nogame"])
    async def free(self, ctx, member: discord.Member, *, message=None):
        """Ping when the user is not playing a game."""
        message = (
            f"{member.mention}, {ctx.author.mention} has sent you a scheduled ping."
            + (f" A message was attached:\n\n```\n{message}\n```" if message else "")
        )
        await ctx.send(
            embed=make_embed(
                title="Ping scheduled",
                description=f"{member.mention} will be pinged when they stop playing a game with the message:\n\n{message}",
                color=colors.EMBED_SUCCESS,
            )
        )
        if member.activity:
            await self.bot.wait_for(
                "member_update",
                check=lambda before, after: after.id == member.id
                and after.activity == None,
            )
        await ctx.send(message)

    @commands.group(aliases=["ev", "feed"])
    async def event(self, ctx):
        """Commands related to events."""

    @event.command(aliases=["add"])
    async def create(self, ctx, name, *, times=""):
        """Create an event.
        If no times are given, the event will only be able to be triggered manually.
        Otherwise, you can schedule triggers, like `3 hours later` or `12:30PM`, seperated by commas.
        If you have a time added with the `time` command, your timezone will be assumed. Otherwise, UTC will be used unless you specify a timezone like `at 12:30PM EST`.
        Example usage: `event create game in two minutes, 6PM`
        """
        if name.lower() in event_config:
            await show_error(ctx, "That event already exists.")

        event = Event(name, [], [], ctx.author.id, [])
        await self.parse_times(ctx, event, times)

        event_config[name.lower()] = event
        saving = {}
        for event in event_config:
            saving[event] = list(event_config[event])
        save_json(paths.EVENT_SAVES, saving)

        await ctx.send(
            embed=make_embed(
                title="Added event",
                description="Your event was created successfully.",
                color=colors.EMBED_SUCCESS,
            )
        )

    @event.command()
    async def remove(self, ctx, event: Event):
        """Remove an event."""
        if ctx.author.id != event.owner:
            await show_error(ctx, "You are not the owner of this event.")

        event_config.pop(event.name.lower())
        saving = {}
        for event in event_config:
            saving[event] = list(event_config[event])
        save_json(paths.EVENT_SAVES, saving)

        await ctx.send(
            embed=make_embed(
                title="Deleted event",
                description="Your event was removed successfully.",
                color=colors.EMBED_SUCCESS,
            )
        )

    @event.command()
    async def schedule(self, ctx, event: Event, *, times):
        """Add more scheduled times to an existing event."""
        if ctx.author.id not in event.managers and ctx.author.id != event.owner:
            await show_error(ctx, "You're not a manager of this event.")

        await self.parse_times(ctx, event, times)
        await ctx.send(
            embed=make_embed(
                title="Scheduled time",
                description="Successfully added a new scheduled time to that event.",
                color=colors.EMBED_SUCCESS,
            )
        )

    @event.command()
    async def trigger(self, ctx, event: Event, *, message=None):
        """Trigger an event manually."""
        if ctx.author.id not in event.managers and ctx.author.id != event.owner:
            await show_error(ctx, "You're not a manager of this event.")

        await self.trigger_event(event, message)

    @event.command(aliases=["sub", "join", "unleave"])
    async def subscribe(self, ctx, event: Event):
        """Subscribe to an event."""
        if str(ctx.author.id) in event.members:
            await show_error(ctx, "You're already subscribed to that event.")

        event.members.append(ctx.author.id)
        saving = {}
        for event in event_config:
            saving[event] = list(event_config[event])
        save_json(paths.EVENT_SAVES, saving)

        await ctx.send(
            embed=make_embed(
                title="Subscribed to event",
                description=(
                    "You were successfully subscribed to that event.\n"
                    "Make sure that the bot is able to DM you, "
                    "i.e. that you haven't blocked it and you have DMs from non-friends enabled on this server."
                ),
                color=colors.EMBED_SUCCESS,
            )
        )

    @event.command(aliases=["unsub", "leave", "unjoin"])
    async def unsubscribe(self, ctx, event: Event):
        """Unsubscribe to an event."""
        if str(ctx.author.id) not in event.members:
            await show_error(ctx, "You're not subscribed to that event.")

        event.members.remove(ctx.author.id)
        saving = {}
        for event in event_config:
            saving[event] = list(event_config[event])
        save_json(paths.EVENT_SAVES, saving)

        await ctx.send(
            embed=make_embed(
                title="Unsubscribed to event",
                description="You were successfully unsubscribed to that event.",
                color=colors.EMBED_SUCCESS,
            )
        )

    @event.group(aliases=["managers"])
    async def manager(self, ctx):
        """Commands related to managers for events; that is, people who are allowed to trigger the event besides the owner."""

    @manager.command()
    async def add(self, ctx, event: Event, member: discord.Member):
        """Add a manager."""
        if ctx.author.id != event.owner:
            await show_error("You are not the owner of this event.")
        if member.id in event.managers:
            await show_error("That member is already a manager of this event.")

        event.managers.append(member.id)
        saving = {}
        for event in event_config:
            saving[event] = list(event_config[event])
        save_json(paths.EVENT_SAVES, saving)

        await ctx.send(
            embed=make_embed(
                title="Added manager",
                description="Successfully added a manager to that event.",
                color=colors.EMBED_SUCCESS,
            )
        )

    @manager.command(name="remove")
    async def remove_(self, ctx, event: Event, member: discord.Member):
        """Remove a manager."""
        if ctx.author.id != event.owner:
            await show_error(ctx, "You are not the owner of this event.")
        if member.id not in event.managers:
            await show_error(ctx, "That member isn't a manager of this event.")

        event.managers.remove(member.id)
        saving = {}
        for event in event_config:
            saving[event] = list(event_config[event])
        save_json(paths.EVENT_SAVES, saving)

        await ctx.send(
            embed=make_embed(
                title="Removed manager",
                description="Successfully removed a manager from that event.",
                color=colors.EMBED_SUCCESS,
            )
        )

    @manager.command()
    async def list(self, ctx, event: Event):
        await ctx.send(
            embed=make_embed(
                title="Managers",
                description="\n".join(
                    [self.bot.get_user(x).mention for x in event.managers]
                ),
                color=colors.EMBED_SUCCESS,
            )
        )

    async def trigger_event(self, event, message=None):
        for id in event.members:
            user = self.bot.get_user(id)
            if not user:
                continue
            await user.send(
                embed=make_embed(
                    title=f"{event.name}",
                    description=message or f"This event has triggered.",
                )
            )

    async def parse_times(self, ctx, event, times):
        for t in times.split(","):
            parsed = dateparser.parse(
                t.strip(),
                settings={
                    "TIMEZONE": self.time_config[str(ctx.author.id)],
                    "TO_TIMEZONE": "UTC",
                },
            )
            if parsed:
                parsed_number = calendar.timegm(parsed.timetuple())
                print(parsed_number, time.time())
                while parsed_number < time.time():
                    parsed_number += 24 * 60 * 60
                event.times.append(parsed_number)
        event.times.sort()

    @tasks.loop(minutes=1)
    async def event_loop(self):
        for event in event_config:
            if (
                event_config[event].times
                and time.time() >= event_config[event].times[0]
            ):
                event_config[event].times.pop(0)
                with open(
                    paths.CONFIG_FOLDER + "/" + paths.EVENT_SAVES, "w"
                ) as f:
                    saving = { }
                    for event in event_config:
                        saving[event] = list(event_config[event])
                    json.dump(saving, f)
                await self.trigger_event(event_config[event])

    @event_loop.before_loop
    async def before_event(self):
        await self.wait_until_ready()


def setup(bot):
    t = Time(bot)
    bot.add_cog(t)
