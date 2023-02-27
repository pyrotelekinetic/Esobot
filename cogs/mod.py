import asyncio
import time
from typing import Union, Optional

import discord
from discord.ext import commands


Targets = commands.Greedy[discord.Member]
HackTargets = commands.Greedy[Union[discord.Member, int]]

class Moderation(commands.Cog):
    """Moderation functionality for the server."""

    def __init__(self, bot):
        self.bot = bot
        self.mute_role = None
        self._emoji = {}

    async def confirm(self, ctx, targets, reason, verb, *, forbidden_fail=True):
        ss = [str(x) if isinstance(x, int) else x.mention for x in targets]
        if len(targets) == 1:
            users = f"the user {ss[0]}"
        else:
            users = f"{len(targets)} users ({', '.join(ss)})"

        embed = discord.Embed(title="Are you sure?", description=f"You are about to {ctx.command.name} {users}. Please confirm the following things.")

        embed.add_field(name="Warned?", value="Have you given the users due warning? If their infractions are minor, consider a verbal caution before taking action.")
        embed.add_field(name="Legitimacy", value=f"Take care not to {ctx.command.name} for insincere reasons such as jokes, as intimidation or due to corruption. \
                                                   Ensure your punishment is proportional to the severity of the rule violation you are punishing.")

        if not reason:
            embed.add_field(name="No reason?", value="Consider adding a reason for your action. This will inform the users of your reasoning, as well as storing it in the audit log for future reference.")
        embed.set_footer(text="If you're certain you want to proceed, click the checkmark emoji below. If you've rethought your decision, click the X.")

        msg = await ctx.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        r, _ = await self.bot.wait_for("reaction_add", check=lambda r, u: str(r.emoji) in ("✅", "❌") and r.message.id == msg.id and u == ctx.author)

        await msg.delete()
        if str(r.emoji) == "✅":
            if reason:
                good = []
                for target in targets:
                    if isinstance(target, int):
                        good.append(discord.Object(id=target))
                    else:
                        try:
                            await target.send(f"You've been {verb} for the following reason: {reason}")
                        except discord.Forbidden:
                            msg = f"Couldn't DM {target}."
                            if forbidden_fail:
                                await ctx.send(msg)
                                continue
                            elif target not in ctx.message.mentions:
                                msg += f" Mentioning instead: {target.mention}"
                                await ctx.send(msg)
                        good.append(target)
                return good
            else:
                return targets
        else:
            return []

    async def perform(self, ctx, unconfirmed_targets, method, verb, reason, confirm=True):
        if confirm:
            targets = await self.confirm(ctx, unconfirmed_targets, reason, verb.lower())
        else:
            targets = unconfirmed_targets
        if not targets:
            return await ctx.send("Nothing to do. Stop.")

        message = []
        successful = []
        for target in targets:
            if ctx.author.top_role <= target.top_role:
                message.append(f"You're a lower rank than {target}.")
                continue
            try:
                await method(target, reason=reason)
            except discord.HTTPException as e:
                message.append(f"Operation failed on {target}: {e}")
            else:
                successful.append(target)

        if successful:
            if len(successful) == 1:
                message.append(f"{verb} {successful[0]}.")
            elif len(successful) == 2:
                message.append(f"{verb} {successful[0]} and {successful[1]}.")
            elif len(successful) < 5:
                message.append(f"{verb} {', '.join(successful[:-1])}, and {successful[-1]}.")
            else:
                message.append(f"{verb} {len(successful)} users.")
        await ctx.send("\n".join(message))

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, targets: HackTargets, *, reason=None):
        """Ban a member."""
        await self.perform(ctx, targets, ctx.guild.ban, "Banned", reason)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, targets: HackTargets, *, reason=None):
        """Unban a user."""
        await self.perform(ctx, targets, ctx.guild.unban, "Unbanned", reason, confirm=False)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, targets: Targets, *, reason=None):
        """Kick a user."""
        await self.perform(ctx, targets, ctx.guild.kick, "Kicked", reason)

    async def emoji_for(self, user):
        emoji_guild = self.bot.get_guild(877165293724631050)
        if user in self._emoji:
            return self._emoji[user]
        for emoji in emoji_guild.emojis:
            if emoji.name == str(user.id):
                self._emoji[user] = emoji
                return emoji
        if len(emoji_guild.emojis) == 50:
            await min(emoji_guild.emojis, key=lambda e: e.created_at).delete(reason="Making space")
        return await emoji_guild.create_custom_emoji(name=str(user.id), image=await user.avatar.read())

    async def move_messages(self, channel, thread, messages):
        webhooks = await channel.webhooks()
        webhook = webhooks[0] if webhooks else await channel.create_webhook(name="Esobot Message Mover")

        for message in messages:
            if message.type not in (discord.MessageType.default, discord.MessageType.reply):
                continue

            content = message.content
            if message.reference and message.reference.resolved:
                reply_content = " ".join(message.reference.resolved.content.splitlines())
                if len(reply_content) > 80:
                    reply_content = reply_content[:80] + "..."
                author = message.reference.resolved.author
                content = (f"[Reply to {await self.emoji_for(author)} **@{author.display_name}**]({message.reference.jump_url}) "
                           f" {reply_content}\n" + content)

            await webhook.send(
                content,
                username=message.author.display_name,
                avatar_url=message.author.avatar,
                files=[await x.to_file() for x in message.attachments],
                embeds=message.embeds,
                thread=thread,
                view=discord.ui.View.from_message(message),
            )

        b = []
        minimum_time = int((time.time() - 14 * 24 * 60 * 60) * 1000.0 - 1420070400000) << 22
        strategy = messages[0].channel.delete_messages
        for message in messages:
            if message.id < minimum_time:
                await strategy(b)
                b = []
                strategy = discord.channel._single_delete_strategy
            b.append(message)
            if len(b) == 100:
                await strategy(b)
                b = []
        await strategy(b)

    @commands.command(aliases=["rmove"])
    @commands.has_permissions(manage_messages=True)
    async def move(self, ctx, msg: Optional[int], where: discord.TextChannel = None):
        await ctx.message.delete()

        start = discord.Object(((msg >> 22) - 10) << 22) if msg else (ctx.message.reference.resolved if ctx.message.reference else None)
        if not start:
            return await ctx.send("I don't know what messages to send.")
        messages = []
        async for m in ctx.channel.history(limit=None, after=start, oldest_first=True):
            if ctx.invoked_with != "rmove" or m.reference and m.reference.resolved in messages:
                messages.append(m)

        view = discord.ui.View()
        event = asyncio.Event()
        view.add_item(StopButton(event, ctx.author))
        m = await ctx.send(f"Moving {len(messages)} messages.", view=view)
        await asyncio.sleep(2)
        if event.is_set():
            return

        if where is None:
            channel = ctx.channel
            try:
                thread = await messages[0].create_thread(name="Moved messages")
            except discord.HTTPException:
                return await ctx.send("That message already has a thread, so I can't make a new one.")
        else:
            channel = where
            thread = None

        done, pending = await asyncio.wait([event.wait(), self.move_messages(channel, thread, messages[bool(thread):])], return_when=asyncio.FIRST_COMPLETED)
        for future in done:
            print(future.exception())
        for future in pending:
            future.cancel()

        await asyncio.sleep(2)
        await m.delete()


class StopButton(discord.ui.Button):
    def __init__(self, event, user):
        self.event = event
        self.user = user
        super().__init__(style=discord.ButtonStyle.danger, label="Stop")

    async def callback(self, interaction):
        if interaction.user != self.user:
            return
        self.event.set()
        self.disabled = True
        await interaction.response.edit_message(content="Cancelled move.", view=self.view)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
