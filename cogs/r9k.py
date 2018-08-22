import copy

from discord.ext import commands
from constants import colors, info, paths, channels
from utils import make_embed, load_json, save_json


messages = set(load_json(paths.R9K_SAVES))

async def close():
    """|coro|
    Closes the connection to discord.
    """
    save_json(paths.R9K_SAVES, list(messages))

    if self.is_closed():
        return

    self._closed.set()

    for voice in self.voice_clients:
        try:
            await voice.disconnect()
        except:
            # if an error happens during disconnects, disregard it.
            pass

    if self.ws is not None and self.ws.open:
        await self.ws.close()


    await self.http.close()
    self._ready.clear()

class R9K:
    """Manage the R9K channel."""

    def __init__(self, bot):
        self.old_bot = copy.copy(bot)
        bot.close = close
        self.bot = bot
        self.channel = bot.get_channel(channels.R9K_CHANNEL)

    def __unload(self):
        self.bot = self.old_bot

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.content in messages:
            await message.delete()
        else:
            messages.add(message.content)


def setup(bot):
    bot.add_cog(R9K(bot))
