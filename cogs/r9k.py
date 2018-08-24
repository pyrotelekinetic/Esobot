import copy
import random

from discord.ext import commands
from constants import colors, info, paths, channels
from utils import make_embed, load_json, save_json


class R9K:
    """Manage the R9K channel."""

    def __init__(self, bot):
        self.bot = bot
        self.channel = bot.get_channel(channels.R9K_CHANNEL)
        self.messages = set(load_json(paths.R9K_SAVES))

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.content in messages:
            await message.delete()
        else:
            messages.add(message.content)
            if random.random() < 0.5:
                save_json(paths.R9K_SAVES, list(messages))


def setup(bot):
    bot.add_cog(R9K(bot))
