import asyncio
import discord

from discord.ext import commands
from utils import make_embed
from constants import colors, info, emoji


class EsobotHelp(commands.MinimalHelpCommand):
    def add_bot_commands_formatting(self, commands, heading):
        if commands:
            self.paginator.add_line(f"**{heading}**")
            self.paginator.add_line("\n".join(f"• ``{c.name}``{' — ' + c.short_doc if c.short_doc else ''}" for c in commands))

    async def send_pages(self):
        dest = self.get_destination()
        for page in self.paginator.pages:
            await dest.send(embed=discord.Embed(title="Help", description=page, color=colors.EMBED_HELP))

    def add_aliases_formatting(self, aliases):
        self.paginator.add_line(f"**Aliases:** ``{'``, ``'.join(aliases)}``", empty=True)

    def add_command_formatting(self, command):
        if command.description:
            self.paginator.add_line(command.description, empty=True)

        signature = self.get_command_signature(command)
        if command.aliases:
            self.paginator.add_line(f"``{signature}``")
            self.add_aliases_formatting(command.aliases)
        else:
            self.paginator.add_line(f"``{signature}``", empty=True)

        if command.help:
            try:
                self.paginator.add_line(command.help, empty=True)
            except RuntimeError:
                for line in command.help.splitlines():
                    self.paginator.add_line(line)
                self.paginator.add_line()


class General(commands.Cog):
    """General-purpose commands."""

    def __init__(self, bot):
        self.bot = bot
        self.original_help = bot.help_command
        bot.help_command = EsobotHelp()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self.original_help

    @commands.command(aliases=["i", "info"])
    async def about(self, ctx):
        """Information about the bot."""
        await ctx.send(
            embed=make_embed(
                title=f"About {info.NAME}",
                description=info.ABOUT_TEXT,
                fields=[
                    ("Author", f"[{info.AUTHOR}]({info.AUTHOR_LINK})", True),
                    ("GitHub Repository", info.GITHUB_LINK, True),
                ],
                footer_text=f"{info.NAME} v{info.VERSION}",
            )
        )

    @commands.command()
    @commands.guild_only()
    async def quote(self, ctx, message: discord.Message):
        """Quote a previous message."""
        embed = make_embed(
            description=message.content,
            timestamp=message.edited_at or message.created_at,
            footer_text="#" + message.channel.name,
        )
        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
        if message.attachments:
            filename = message.attachments[0].filename
            if (
                filename.endswith(".png")
                or filename.endswith(".jpg")
                or filename.endswith(".jpeg")
            ):
                embed.set_image(url=message.attachments[0].url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))
