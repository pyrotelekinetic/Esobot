import copy
import random

from discord.ext import commands
from constants import colors, info, paths, channels
from utils import make_embed, load_json, save_json


class R9K:
    """Manage the R9K channel."""

    def __init__(self, bot):
        self.bot = bot
        self.messages = set(load_json(paths.R9K_SAVES))

    async def on_message(self, message):
        await self.check_message(message)

    async def on_message_edit(self, before, after):
        await self.check_message(after)

    async def check_message(self, message):
        if message.author.bot or message.channel != self.bot.get_channel(channels.R9K_CHANNEL):
            return

        if message.content in self.messages:
            await message.delete()
            print("h")
        else:
            self.messages.add(message.content)
            if random.random() < 0.5:
                save_json(paths.R9K_SAVES, list(self.messages))


def setup(bot):
    bot.add_cog(R9K(bot))
