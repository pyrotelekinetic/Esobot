import random
from collections import defaultdict
from typing import Union

import discord
from discord.ext import commands

from utils import get_pronouns


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

    @commands.group(invoke_without_command=True)
    @commands.dm_only()
    async def anon(self, ctx, target: Union[discord.User, discord.TextChannel, discord.Thread]):
        if isinstance(target, discord.User) and target.bot:
            return await ctx.send("That's a bot, silly!")
        name = rand_name([name for name, _ in self.targets[target]])
        if (k := self.sessions.pop(ctx.author, None)):
            name, target = k
            self.targets[target].remove((name, ctx.author))
        self.sessions[ctx.author] = name, target
        self.targets[target].append((name, ctx.author))
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
                       "Do `!anon stop` to stop bridging.\n"
                       "Note: There is automatic normalization of orthography applied to each message (removing apostrophes, commas, question marks, and periods; and lowercasing everything). "
                       r"You can avoid this for a single message by prefixing it with a backspace character (\\).")

    @anon.command()
    @commands.dm_only()
    async def stop(self, ctx):
        try:
            name, target = self.sessions.pop(ctx.author)
        except KeyError:
            await ctx.send("?")
        else:
            self.targets[target].remove((name, ctx.author))
            await ctx.send("Stopped.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild and message.author in self.sessions and not message.content.startswith("!"):
            name, target = self.sessions[message.author]
            content = message.content
            if content.startswith("\\"):
                content = content[1:]
            else:
                content = content.lower().replace(",", "").replace("'", "").replace(".", "").replace("?", "")
            await target.send(f"<{name}> {content}", embeds=message.embeds, files=[await f.to_file() for f in message.attachments])
        if message.author == self.bot.user and message.content.startswith("<"):
            return
        for _, person in self.targets[message.channel if message.guild else message.author]:
            await person.send(f"<{message.author.display_name}> {message.content}", embeds=message.embeds, files=[await f.to_file() for f in message.attachments])

def setup(bot):
    bot.add_cog(Anonymity(bot))
