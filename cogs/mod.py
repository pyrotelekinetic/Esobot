from typing import Union

import discord
from discord.ext import commands


Targets = commands.Greedy[discord.Member]
HackTargets = commands.Greedy[Union[discord.Member, int]]

class Moderation(commands.Cog):
    """Moderation functionality for the server."""

    def __init__(self, bot):
        self.bot = bot
        self.mute_role = None

    async def confirm(self, ctx, targets, reason, *, forbidden_fail=True):
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

    async def perform(self, ctx, unconfirmed_targets, method, verb, reason, confirm=True):
        if confirm:
            targets = await self.confirm(ctx, unconfirmed_targets, reason)
        else:
            targets = unconfirmed_targets

        message = []
        successful = []
        for target in targets:
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


def setup(bot):
    bot.add_cog(Moderation(bot))
