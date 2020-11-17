import string

from discord.ext import commands
from constants import paths, channels
from utils import load_json, save_json
from unidecode import unidecode


def strip_content(s):
    return "".join([x for x in unidecode(s.strip().casefold()) if x in string.ascii_letters + string.digits])

class R9K(commands.Cog):
    """Manage the R9K channel."""

    def __init__(self, bot):
        self.bot = bot
        self.messages = set(load_json(paths.R9K_SAVES))

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.check_message(message)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if strip_content(before.content) != strip_content(after.content):
            await self.check_message(after)

    async def check_message(self, message):
        if message.author.bot or message.channel != self.bot.get_channel(channels.R9K_CHANNEL):
            return

        stripped_content = strip_content(message.content)

        if stripped_content in self.messages:
            await message.delete()
        else:
            self.messages.add(stripped_content)
            save_json(paths.R9K_SAVES, list(self.messages))


def setup(bot):
    bot.add_cog(R9K(bot))
