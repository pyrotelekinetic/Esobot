import copy
import string

from discord.ext import commands
from constants import colors, info, paths, channels
from utils import make_embed, load_json, save_json
from unidecode import unidecode


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
        await self.check_message(after)

    async def check_message(self, message):
        if message.author.bot or message.channel != self.bot.get_channel(channels.R9K_CHANNEL):
            return

        stripped_content = "".join([x for x in unidecode(message.content.strip().casefold()) if x in string.ascii_letters])

        if stripped_content in self.messages:
            await message.delete()
        else:
            self.messages.add(stripped_content)
            save_json(paths.R9K_SAVES, list(self.messages))


def setup(bot):
    bot.add_cog(R9K(bot))
