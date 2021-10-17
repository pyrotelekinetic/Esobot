#!/usr/bin/env python3

import asyncio
import discord
import logging
import sys
import traceback
import os

from cogs import get_extensions
from constants import colors, info, paths
from discord.ext import commands
from utils import l, make_embed, report_error, ShowErrorException

LOG_LEVEL_API = logging.WARNING
LOG_LEVEL_BOT = logging.INFO
LOG_FMT = "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"


try:
    import discord
    import asyncio
except ImportError:
    print("discord.py is required. Run `python3 -m pip install -U discord.py`.")
    exit(1)

try:
    with open("token.txt") as f:
        TOKEN = f.read().strip()
except IOError:
    print("Create a file token.txt and place the bot token in it.")
    exit(1)

if not os.path.exists(paths.CONFIG_FOLDER):
    os.makedirs(paths.CONFIG_FOLDER)
for file in paths.SAVE_FILES:
    if not os.path.exists(paths.CONFIG_FOLDER + "/" + file):
        with open(paths.CONFIG_FOLDER + "/" + file, "w") as f:
            f.write(paths.SAVE_FILES[file])


if info.DEV:
    logging.basicConfig(format=LOG_FMT)
else:
    logging.basicConfig(format=LOG_FMT, filename="bot.log")
logging.getLogger("discord").setLevel(LOG_LEVEL_API)
l.setLevel(LOG_LEVEL_BOT)


try:
    with open("admin.txt") as f:
        owner_id = int(f.read())
except IOError:
    owner_id = None

COMMAND_PREFIX = "!"

intents = discord.Intents(
    guilds=True,
    members=True,
    messages=True,
    reactions=True,
    emojis=True,
)

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(COMMAND_PREFIX),
    case_insensitive=True,
    status=discord.Status.dnd,
    allowed_mentions=discord.AllowedMentions(everyone=False),
    intents=intents
)
bot.load_extension("jishaku")
bot.owner_id = owner_id
bot.needed_extensions = set(get_extensions())
bot.loaded_extensions = set()


@bot.event
async def on_ready():
    bot.owner_id = (await bot.application_info()).owner.id
    l.info(f"Ready")
    await wait_until_loaded()
    await bot.change_presence(status=discord.Status.online)


@bot.event
async def on_connect():
    l.info(f"Connected as {bot.user}")
    await wait_until_loaded()
    await bot.change_presence(status=discord.Status.idle)


@bot.event
async def on_resumed():
    await wait_until_loaded()
    await bot.change_presence(status=discord.Status.online)
    l.info("Resumed session")


@bot.event
async def on_command_error(ctx, exc):
    if isinstance(exc, commands.CommandInvokeError) and isinstance(
        exc.original, ShowErrorException
    ):
        return

    command_name = ctx.command.name if ctx.command else "unknown command"
    if isinstance(exc, commands.UserInputError):
        if isinstance(exc, commands.MissingRequiredArgument):
            description = f"Missing required argument `{exc.param.name}`."
        elif isinstance(exc, commands.BadArgument):
            description = f"Invalid argument. {str(exc)}"
        else:
            description = f"Unknown user input exception."
        description += f"\n\nRun `{COMMAND_PREFIX}help {command_name}` to view the required arguments."
    elif isinstance(exc, commands.CommandNotFound):
        # description = f"Could not find command `{ctx.invoked_with.split()[0]}`."
        return
    elif isinstance(exc, commands.CheckFailure):
        if isinstance(exc, commands.NoPrivateMessage):
            description = "Cannot be run in a private message channel."
        elif isinstance(exc, commands.MissingPermissions):
            description = "You don't have permission to do that. "
            missing_perms = ", ".join(exc.missing_perms)
            description += f"Missing {missing_perms}"
        elif isinstance(exc, commands.NotOwner):
            description = "You have to be the bot owner to do that."
        elif isinstance(exc, commands.MissingRole):
            description = f"You're missing the required role '{exc.missing_role}'."
        else:
            description = "Command check failed. For one reason or another, you're not allowed to run that command in this context."
    elif isinstance(exc, commands.DisabledCommand):
        description = "That command is disabled."
    elif isinstance(exc, commands.CommandOnCooldown):
        description = f"That command is on cooldown. Try again in {exc.retry_after:.1f} seconds."
    elif isinstance(exc, commands.MaxConcurrencyReached):
        description = "This command is currently already in use. Please try again later."
    else:
        description = "Sorry, something went wrong."
        l.error(
            f"Unknown error encountered while executing '{command_name}'\n" + "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        )
    await ctx.send(
        embed=make_embed(
            color=colors.EMBED_ERROR, title="Error", description=description
        )
    )


@bot.event
async def on_error(event_method, *args, **kwargs):
    l.error(
        f"Error encountered during '{event_method}' (args: {args}; kwargs: {kwargs})\n" + traceback.format_exc()
    )


async def load_extensions(extensions):
    for extension in extensions:
        await asyncio.sleep(0)
        try:
            bot.load_extension("cogs." + extension)
        except Exception as e:
            print(f"Failed to load {extension}: {type(e).__name__}: {e}")
            continue
        bot.loaded_extensions.add(extension)
    l.info("Loaded all extensions")


async def wait_until_loaded():
    while bot.needed_extensions < bot.loaded_extensions:
        await asyncio.sleep(0)


if __name__ == "__main__":
    bot.loop.create_task(load_extensions(bot.needed_extensions))
    bot.run(TOKEN)
