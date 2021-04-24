from typing import Union

import discord
from discord.ext import commands


Targets = commands.Greedy[discord.Member]
HackTargets = commands.Greedy[Union[discord.Member, int]]

async def say_count(ctx, verb, l):
    count = len(l)
    if count > 1:
        await ctx.send(f"{verb} {count} users.")
    elif count == 1:
        await ctx.send(f"{verb} {l[0]}.")

class Moderation(commands.Cog):
    """Moderation functionality for the server."""

    def __init__(self, bot):
        self.bot = bot
        self.mute_role = None

    async def confirm(self, ctx, targets, reason, *, forbidden_fail=False):
        ss = [str(x) if isinstance(x, int) else x.mention for x in targets]
        if len(targets) == 1:
            users = f"the user {ss[0]}"
        else:
            users = f"{len(targets)} users ({', '.join(ss)})"

        embed = discord.Embed(title="Are you sure?", description=f"You are about to {ctx.command.name} {users}. Please confirm the following things.")

        embed.add_field(name="Warned?", value="Have you given the user due warning? If their infraction is minor, consider a verbal caution before taking action.")
        embed.add_field(name="Legitimacy", value=f"Take care not to {ctx.command.name} for insincere reasons such as jokes, as intimidation or due to corruption. \
                                                   Ensure your punishment is proportional to the severity of the rule violation you are punishing.")

        if not reason:
            embed.add_field(name="No reason?", value="Consider adding a reason for your action. This will inform the user of your reasoning, as well as storing it in the audit log for future reference.")
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
                            await target.send(f"A {ctx.command.name} is being performed on you for the following reason: {reason}")
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

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, targets: HackTargets, *, reason=None):
        """Ban a member."""
        confirmed_targets = await self.confirm(ctx, targets, reason, forbidden_fail=True)
        for target in confirmed_targets:
            if ctx.author.top_role <= target.top_role:
                await ctx.send(f"Your rank isn't higher than {target}'s.")
            try:
                await ctx.guild.ban(target, reason=reason)
            except discord.HTTPException:
                await ctx.send(f"Couldn't ban {target}.")
        await say_count(ctx, "Banned", confirmed_targets)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, targets: HackTargets, *, reason=None):
        """Unban a user."""
        for target in targets:
            try:
                await ctx.guild.unban(target, reason=reason)
            except discord.HTTPException:
                await ctx.send(f"Couldn't unban {target}.")
        await say_count(ctx, "Unbanned", targets)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, targets: Targets, *, reason=None):
        """Kick a user."""
        confirmed_targets = await self.confirm(ctx, targets, reason, forbidden_fail=True)
        for target in confirmed_targets:
            if ctx.author.top_role <= target.top_role:
                await ctx.send(f"Your rank isn't higher than {target}'s.")
            try:
                await target.kick(reason=reason)
            except discord.HTTPException:
                await ctx.send(f"Couldn't kick {target}.")
        await say_count(ctx, "Kicked", confirmed_targets)


def setup(bot):
    bot.add_cog(Moderation(bot))
