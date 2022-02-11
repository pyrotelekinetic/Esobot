import random
from collections import defaultdict
from typing import Union, Optional

import discord
from discord.ext import commands

from utils import get_pronouns, load_json, save_json
from constants.paths import ANON_SAVES


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
        self.data = load_json(ANON_SAVES)

        # LOL
        allow = []
        deny = []
        conns = []
        for t in self.data["allow"]:
            allow.append(tuple(t))
        for t in self.data["deny"]:
            deny.append(tuple(t))
        for t in self.data["conns"]:
            conns.append(tuple(t))
        self.data["allow"] = allow
        self.data["deny"] = deny
        self.data["conns"] = conns

    def save(self):
        save_json(ANON_SAVES, self.data)

    @property
    def conns(self):
        return self.data["conns"]

    @property
    def names(self):
        return self.data["names"]

    @property
    def allow(self):
        return self.data["allow"]

    @property
    def deny(self):
        return self.data["deny"]

    def match_pat(self, pred, pat):
        pred1, pred2 = pred
        pat1, pat2 = pat
        return (pat1 is None or pred1 == pat1) and (pat2 is None or pred2 == pat2)

    async def ensure_channel(self, channel_or_user):
        if isinstance(channel_or_user, discord.User):
            channel = await channel_or_user.create_dm()
        else:
            channel = channel_or_user
        return channel

    def pat_ids(self, ts):
        return (ts[0].id if ts[0] else None, ts[1].id if ts[1] else None)

    def pred_objs(self, pred):
        return (self.bot.get_user(pred[0]), self.bot.get_partial_messageable(pred[1]))

    def name_for(self, user):
        return self.names[str(user.id)][0]

    def one_with_name(self, target_name):
        for user, name in self.names.items():
            if name[0] == target_name:
                return self.bot.get_user(int(user))
        return None

    def refresh_names(self):
        for l in self.names.values():
            l[1] = True
        self.save()

    def targeting(self, t):
        return [targeting for targeting, target in self.conns if target == t.id]

    def add_rule(self, rules, pat, tag):
        to_add = *pat, tag
        if tag is None:
            if to_add in rules:
                return False
        else:
            if any(this_tag == tag for _, _, this_tag in rules):
                return False
        rules.append(to_add)
        return True

    def remove_rule(self, rules, pat, tag):
        if tag is None:
            try:
                rules.remove((*pat, tag))
            except ValueError:
                return False
            else:
                return True
        else:
            for i, (_, _, this_tag) in enumerate(rules):
                if this_tag == tag:
                    rules.pop(i)
                    return True
            return False

    def disable(self, pat, tag=None):
        l = [self.end_session(x) for x in self.connections(pat)]
        pat = self.pat_ids(pat)
        self.remove_rule(self.allow, pat, tag)
        if self.add_rule(self.deny, pat, tag):
            self.save()  # it looks like this save is in the wrong place but it's actually fine
            return l
        else:
            return None

    def enable(self, pat, tag=None):
        pat = self.pat_ids(pat)
        self.remove_rule(self.deny, pat, tag)
        r = self.add_rule(self.allow, pat, tag)
        self.save()
        return not r

    def start_session(self, targeting, target):
        k = (targeting.id, target.id)
        if not any(self.match_pat(k, x[:2]) for x in self.allow) or any(self.match_pat(k, x[:2]) for x in self.deny):
            return None
        new = (targeting.id, target.id)
        if new in self.conns:
            return (None, None)
        if self.names.get(str(targeting.id), (None, True))[1]:
            self.names[str(targeting.id)] = [rand_name(self.names.values()), False]
        old = self.end_session((targeting, None))
        self.conns.append(new)
        self.save()
        return (old, target)

    def end_session(self, pat):
        pat = self.pat_ids(pat)
        for i, pred in enumerate(self.conns):
            if self.match_pat(pred, pat):
                self.conns.pop(i)
                r = self.pred_objs(pred)
                self.save()
                return r
        return None

    def connections(self, pat):
        pat = self.pat_ids(pat)
        l = []
        for pred in self.conns:
            if self.match_pat(pred, pat):
                objs = self.pred_objs(pred)
                if objs[0]:
                    l.append(objs)
        return l

    async def take_user_arg(self, ctx, name, context=None):
        n = self.one_with_name(name)
        tag = name
        dn = name
        if not n:
            n = await commands.UserConverter().convert(ctx, name)
            if n.bot:
                await ctx.send("That's a bot.")
                # muahaha
                raise commands.CommandNotFound()
            tag = n.id
            dn = n.display_name
        return n, [*context, tag], dn

    @commands.dm_only()
    @commands.group(invoke_without_command=True)
    async def anon(self, ctx, target: Union[discord.User, discord.TextChannel, discord.Thread]):
        """Use in DMs with Esobot to anonymously message a user or channel."""
        if isinstance(target, discord.User) and target.bot:
            return await ctx.send("That's a bot, silly!")
        if not (isinstance(target, discord.User) or (member := target.guild.get_member(ctx.author.id)) and target.permissions_for(member).send_messages):
            return await ctx.send("You can't speak in that channel.")

        if isinstance(target, discord.User) and self.connections((None, await self.ensure_channel(ctx.author))):
            return await ctx.send("You can't talk to another user anonymously while you're already being talked to by someone else.")
        if isinstance(target, discord.User) and any([isinstance(self.bot.get_channel(targeted.id), (discord.DMChannel, type(None))) for _, targeted in self.connections((target, None))]):
            return await ctx.send("You can't talk to this user; they're already talking to someone else anonymously.")

        o = self.start_session(ctx.author, await self.ensure_channel(target))
        if not o:
            if isinstance(target, discord.User):
                p = get_pronouns(target)
                return await ctx.send(f"You are blocked or that person is not accepting anonymous connections. Consider contacting {p.obj} to get {p.obj} to opt into anonymous messaging. Don't blow your cover, though!")
            else:
                return await ctx.send("You are blocked or anonymous connections are not enabled for that channel. Consider contacting the server admins to get them to enable it. Don't blow your cover, though!")

        name = self.name_for(ctx.author)
        old, new = o
        if not new:
            return await ctx.send("But nothing changed.")
        if old:
            await old[1].send(f"{self.name_for(old[0])} left.")

        if isinstance(target, discord.User):
            p = get_pronouns(target)
            where = f"to {p.obj}"
            prep = "with"
            await new.send(f"You are being messaged anonymously by '{name}'.")
        else:
            where = "there"
            prep = "in"
            await new.send(f"An anonymous user ({name}) joined the channel.")

        await ctx.send(f"Started a session {prep} {target.mention}. All the messages you send (except commands) after this point will be sent {where}.\n"
                       f"You are *{name}*. Do `!anon leave` to stop bridging.\n"
                       "Note: Automatic normalization of orthography is applied to each message. "
                       "Avoid this for a single message by prefixing it with `\\`.\n"
                       "**NB**: Full anonymity is not guaranteed. Your identity can be accessed by the developer of the bot.\n"
                       "**NB**: If you inadvertently reveal your own identity, contact LyricLy so she can refresh the names. Post-refresh, you'll get a new name when you next use `anon`.")

    @commands.dm_only()
    @anon.command(aliases=["stop"])
    async def leave(self, ctx):
        """Leave a channel which you are anonymously messaging."""
        if p := self.end_session((ctx.author, None)):
            await p[1].send(f"{self.name_for(p[0])} left.")
            await ctx.send("Left.")
        else:
            await ctx.send("?")

    @commands.dm_only()
    @anon.command(aliases=["hide", "cower", "opt-out", "out"])
    async def optout(self, ctx):
        """Opt out of being anonymously messaged in your DMs. Undoes `optin`."""
        l = self.disable((None, await self.ensure_channel(ctx.author)))
        if l is None:
            return await ctx.send("?")
        for u in l:
            await u[0].send("Your anonymous session was forcibly closed by the recipient opting out.")
        names = [self.name_for(x[0]) for x in l]
        match names:
            case []:
                report = ""
            case [x]:
                report = f" and disconnected {x}"
            case [x, y]:
                report = f" and disconnected {x} and {y}"
            case [*xs, y]:
                report = f" and disconnected {', '.join(xs)}, and {y}"
        await ctx.send(f"Alright. Stopped incoming connections{report}.")

    @commands.dm_only()
    @anon.command(aliases=["unhide", "return", "opt-in", "in"])
    async def optin(self, ctx):
        """Opt in to receiving messages anonymously in your DMs."""
        if self.enable((None, await self.ensure_channel(ctx.author))):
            return await ctx.send("?")
        await ctx.send("Enabled. Good luck.")

    @commands.dm_only()
    @anon.command()
    async def block(self, ctx, *, name):
        """Block a particular anonymous user to stop them DMing you."""
        
        n, tag, dn = await self.take_user_arg(ctx, name, ("block", ctx.author.id))

        l = self.disable((n, await self.ensure_channel(ctx.author)), tag)
        if l is None:
            return await ctx.send("You already have them blocked.")
        for u in l:
            await u[0].send("Your anonymous session was forcibly closed by the recipient blocking you.")

        report = " and disconnected them"*(bool(l) and isinstance(n, str))
        await ctx.send(f"Alright. Blocked {dn}{report}.")

    @commands.dm_only()
    @anon.command()
    async def unblock(self, ctx, *, name):
        """Unblock a user. Undoes `block`."""
        n, tag, dn = await self.take_user_arg(ctx, name, ("block", ctx.author.id))
        if self.enable((n, await self.ensure_channel(ctx.author)), tag):
            return await ctx.send("They weren't blocked.")
        await ctx.send(f"Okay, {dn} can message you anonymously now.")

    @commands.has_permissions(manage_channels=True)
    @anon.command(name="enable")
    async def _enable(self, ctx, *, channel: discord.TextChannel = None):
        """Let a channel be messaged anonymously."""
        channel = channel or ctx.channel
        if self.enable((None, channel)):
            return await ctx.send("That was already enabled, but I double-enabled it to make sure.\n(Narrator: It did not.)")
        await ctx.send("Enjoy the spam or whatever.")

    @commands.has_permissions(manage_channels=True)
    @anon.command(name="disable")
    async def _disable(self, ctx, *, channel: discord.TextChannel = None):
        """The inverse of `enable`."""
        channel = channel or ctx.channel
        l = self.disable((None, channel))
        if l is None:
            return await ctx.send("Wasn't enabled in the first place, but okay.")
        for u in l:
            await u[0].send("Your anonymous session was closed forcibly because the channel's access was disabled.")
        await ctx.send("No more spam.")

    @commands.has_permissions(kick_members=True)  # I'd like this to be timeouts but dpy of course doesn't have the perm
    @anon.command()
    async def unmute(self, ctx, channel: Optional[discord.TextChannel] = None, *, name):
        """Unmute a user, reversing `mute`."""
        channel = channel or ctx.channel
        n, tag, _ = await self.take_user_arg(ctx, name, ("mute", channel.id))
        if self.enable((n, channel), tag):
            return await ctx.send("They weren't muted.")
        await ctx.send("They're back.")

    @commands.has_permissions(kick_members=True)
    @anon.command()
    async def mute(self, ctx, channel: Optional[discord.TextChannel] = None, *, name):
        """Mute a user in a single channel, stopping them from being able to use anonymous messaging there."""
        channel = channel or ctx.channel
        n, tag, _ = await self.take_user_arg(ctx, name, ("mute", channel.id))
        l = self.disable((n, channel), tag)
        if l is not None:
            for u in l:
                await u[0].send("Your anonymous session was closed forcibly because you were muted.")
        await ctx.send("They're gone.")

    @anon.command(aliases=["list"])
    async def who(self, ctx):
        """List the anonymous users connected to the current channel."""
        names = [self.name_for(x[0]) for x in self.connections((None, ctx.channel))]
        if not names:
            await ctx.send("There's nobody here.")
        else:
            await ctx.send(f"{len(names)} user{'s'*(len(names)>1)} connected ({', '.join(names)})")

    @commands.is_owner()
    @anon.command()
    async def halt(self, ctx, *, name):
        n, _, _ = await self.take_user_arg(ctx, name)
        l = self.disable((n, None))
        if l is None:
            return await ctx.send("Not sure how you forgot that you already did that, but yeah, they were already super banned.")
        for u in l:
            await u[0].send("Your anonymous session was closed forcibly because you were banned from the entire bot. Well done.")
        await ctx.send("They're gone for good. Unless you let them come back.")

    @commands.is_owner()
    @anon.command()
    async def unhalt(self, ctx, *, name):
        n, _, _ = await self.take_user_arg(ctx, name)
        if self.enable((n, None)):
            return await ctx.send("No, they were alright, actually. They weren't banned.")
        await ctx.send("'Tis the season for forgiveness. Unless it isn't Christmas time any more. It roughly was at the time of writing. Anyway, they're unbanned.")

    @commands.is_owner()
    @anon.command(aliases=["uncover", "reveal", "deanon", "de"])
    async def see(self, ctx, *, target_name):
        if not (u := self.one_with_name(target_name)):
            return await ctx.send("Nobody here is called that.")
        await ctx.send(f"That's {u}.")

    @commands.is_owner()
    @anon.command()
    async def refresh(self, ctx):
        self.refresh_names()
        await ctx.send("Done.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild and not message.content.startswith("!") and (t := self.connections((message.author, None))):
            target = t[0][1]
            content = message.content
            if content.startswith("\\"):
                content = content[1:]
            else:
                content = content.lower().replace(",", "").replace("'", "").replace(".", "").replace("?", "")
            await target.send(f"<{self.name_for(message.author)}> {content}", embeds=message.embeds, files=[await f.to_file() for f in message.attachments])

        for connection in self.connections((None, message.channel)):
            # don't relay our own relays
            if message.author == self.bot.user and message.content.startswith(f"<{self.name_for(connection[0])}>"):
                continue
            # don't relay ourselves in DMs
            if not message.guild and (message.author == self.bot.user or message.content.startswith("!")):
                continue
            try:
                await connection[0].send(f"<{message.author.display_name}> {message.content}", embeds=message.embeds, files=[await f.to_file() for f in message.attachments])
            except discord.Forbidden:
                pass

def setup(bot):
    bot.add_cog(Anonymity(bot))
