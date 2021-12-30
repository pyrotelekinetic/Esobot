import random
from collections import defaultdict
from typing import Union

import discord
from discord.ext import commands

from utils import get_pronouns, aggressive_normalize


def rand_name(taken_names):
    name = ""
    for i in range(2, 4):
        syllable = "ji"
        while syllable[:2] in ("ji", "wo", "wo", "ti"):
            syllable = random.choice("ptkswlj" if name.endswith("n") else "mnptkswlj") + random.choice("aeiou") + "n"*random.randint(0, 1)
        name += syllable
    name = f"jan {name.capitalize()}"
    return name if name not in taken_names else rand_name(taken_names)


class Anonymity(commands.Cog):
    """Send messages anonymously."""

    def __init__(self, bot):
        self.bot = bot
        self.sessions = {}
        self.targets = defaultdict(list)
        self.hiding = set()

    def end_session(self, user):
        try:
            name, target = self.sessions.pop(user)
        except KeyError:
            return None
        self.targets[target].remove((name, user))
        return name, target

    @commands.group(invoke_without_command=True)
    @commands.dm_only()
    async def anon(self, ctx, target: Union[discord.User, discord.TextChannel, discord.Thread]):
        """Use in DMs with Esobot to anonymously message a user or channel."""
        if isinstance(target, discord.User) and target.bot:
            return await ctx.send("That's a bot, silly!")
        if not (isinstance(target, discord.User) or (member := target.guild.get_member(ctx.author.id)) and target.permissions_for(member).send_messages):
            return await ctx.send("You can't speak in that channel.")
        if target in self.hiding:
            return await ctx.send("Recipient is not accepting anonymous connections.")

        p = self.end_session(ctx.author)
        if p and p[1] == target:
            name = p[0]
            still = True
        else:
            name = rand_name([name for name, _ in self.targets[target]])
            still = False
            if p:
                await p[1].send(f"{p[0]} left.")

        self.sessions[ctx.author] = name, target
        self.targets[target].append((name, ctx.author))

        if still:
            return await ctx.send("But nothing changed.")

        if isinstance(target, discord.User):
            p = get_pronouns(target)
            where = f"to {p.obj}"
            prep = "with"
            await target.send(f"You are being messaged anonymously by '{name}'.")
        else:
            where = "there"
            prep = "in"
            await target.send(f"An anonymous user ({name}) joined the channel.")

        await ctx.send(f"Started an anonymous messaging session {prep} {target.mention}. All the messages you send (except commands) after this point will be sent {where}.\n"
                       "Do `!anon leave` to stop bridging.\n"
                       "Note: There is automatic normalization of orthography applied to each message (removing apostrophes, commas, question marks, and periods; and lowercasing everything). "
                       r"You can avoid this for a single message by prefixing it with a backspace character (\\).")

    @anon.command(aliases=["stop"])
    @commands.dm_only()
    async def leave(self, ctx):
        """Leave a channel which you are anonymously messaging."""
        if p := self.end_session(ctx.author):
            await p[1].send(f"{p[0]} left.")
            await ctx.send("Left.")
        else:
            await ctx.send("?")

    @anon.command(aliases=["cower"])
    @commands.dm_only()
    async def hide(self, ctx):
        """Opt out of being anonymously messaged in your DMs. Undo with `unhide`."""
        if ctx.author in self.hiding:
            return await ctx.send("?")
        names = []
        ended = []
        for user, (name, target) in self.sessions.items():
            if target == ctx.author:
                names.append(name)
                ended.append(user)
                await user.send("Your anonymous session was forcibly closed by the recipient.")
        for ended in ended:
            self.end_session(ended)
        self.hiding.add(ctx.author)
        match names:
            case []:
                report = ""
            case [x]:
                report = f" and disconnected {x}"
            case [x, y]:
                report = f" and disconnected {x} and {y}"
            case [*xs, y]:
                report = f" and disconnected {', '.join(xs)}, and {y}"
        await ctx.send(f"Alright, coward. Started blocking incoming connections{report}.")

    @anon.command(aliases=["return"])
    @commands.dm_only()
    async def unhide(self, ctx):
        """Reverse the effects of `hide`."""
        if ctx.author not in self.hiding:
            return await ctx.send("?")
        self.hiding.remove(ctx.author)
        await ctx.send("You're no longer a coward.")

    @anon.command(aliases=["list"])
    async def who(self, ctx):
        """List the anonymous users connected to the current channel."""
        names = []
        for name, target in self.sessions.values():
            if target == ctx.channel if ctx.guild else target == ctx.author:
                names.append(name)
        if not names:
            await ctx.send("There's nobody here.")
        else:
            await ctx.send(f"{len(names)} user{'s'*(len(names)>1)} connected ({', '.join(names)})")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild and message.author in self.sessions and not message.content.startswith("!"):
            name, target = self.sessions[message.author]
            content = message.content
            if content.startswith("\\"):
                content = content[1:]
            else:
                content = content.lower().replace(",", "").replace("'", "").replace(".", "").replace("?", "")
            if "smig" in aggressive_normalize(content):
                await message.channel.send("No.")
            else:
                await target.send(f"<{name}> {content}", embeds=message.embeds, files=[await f.to_file() for f in message.attachments])

        for name, person in self.targets[message.channel if message.guild else message.author]:
            if message.author == self.bot.user and message.content.startswith(f"<{name}>") or not message.guild and message.content.startswith("!"):
                continue
            await person.send(f"<{message.author.display_name}> {message.content}", embeds=message.embeds, files=[await f.to_file() for f in message.attachments])

def setup(bot):
    bot.add_cog(Anonymity(bot))
