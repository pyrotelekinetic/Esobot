import discord
from discord.ext import commands
from constants import colors, paths, channels
from utils import make_embed, load_json, save_json, show_error


class Hub(commands.Cog):
    """Manage the hub channel."""

    def __init__(self, bot):
        self.bot = bot
        self.hub_entries, self.hub_queue = load_json(paths.HUB_SAVES)

    def save(self):
        save_json(paths.HUB_SAVES, [self.hub_entries, self.hub_queue])

    @commands.group(invoke_without_command=True)
    async def hub(self, ctx):
        f"""Commands for managing #hub."""
        await ctx.send_help(ctx.command)

    @hub.command()
    async def submit(self, ctx, invite: discord.Invite, *, blurb):
        """Suggest a guild to be linked in the hub channel.
        After suggestion, the admins will look over your request and add it to #hub if it is deemed relevant.
        Please only suggest guilds that are related to esolangs or hobbyist programming in some way.
        """
        msg = await self.bot.get_channel(channels.HUB_QUEUE_CHANNEL).send(embed=make_embed(title=invite.guild.name, url=invite.url, description=blurb))
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        self.hub_queue[str(msg.id)] = {"blurb": blurb, "name": invite.guild.name, "url": invite.url}
        await ctx.send(embed=make_embed(title="Success", description="Your hub entry has been submitted.", color=colors.EMBED_SUCCESS))
        self.save()

    @commands.has_role("Administrators")
    @hub.command(aliases=["remove"])
    async def delete(self, ctx, id: int):
        try:
            self.hub_entries.pop(str(id))
        except KeyError:
            return await show_error(ctx, "That ID isn't a hub entry.")
        await self.bot.http.delete_message(channels.HUB_CHANNEL, id)
        await ctx.send(embed=make_embed(title="Success", description="Deleted hub entry.", color=colors.EMBED_SUCCESS))
        self.save()

    @commands.has_role("Administrators")
    @hub.command(aliases=["modify"])
    async def edit(self, ctx, id: int, *, new_blurb):
        try:
            entry = self.hub_entries[str(id)]
        except KeyError:
            return await show_error(ctx, "That ID isn't a hub entry.")
        await self.bot.http.edit_message(channels.HUB_CHANNEL, id, embed=make_embed(title=entry["name"], url=entry["url"], description=new_blurb).to_dict())
        entry["blurb"] = new_blurb
        await ctx.send(embed=make_embed(title="Success", description="Edited hub entry.", color=colors.EMBED_SUCCESS))
        self.save()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if str(payload.message_id) not in self.hub_queue or payload.user_id == self.bot.user.id:
            return

        if str(payload.emoji) == "✅":
            entry = self.hub_queue.pop(str(payload.message_id))
            msg = await self.bot.get_channel(channels.HUB_CHANNEL).send(embed=make_embed(title=entry["name"], url=entry["url"], description=entry["blurb"]))
            self.hub_entries[str(msg.id)] = entry
        elif str(payload.emoji) == "❌":
            self.hub_queue.pop(str(payload.message_id))
        else:
            return
        await self.bot.http.delete_message(channels.HUB_QUEUE_CHANNEL, payload.message_id)
        self.save()


async def setup(bot):
    await bot.add_cog(Hub(bot))
