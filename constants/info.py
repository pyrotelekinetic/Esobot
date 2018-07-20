import os

DEV = "ESOBOT_DEV" in os.environ

NAME = 'Esobot'
VERSION = '1.3.0' + ('-dev' * DEV)

ABOUT_TEXT = f'''\
{NAME} is an open source Discord bot created using \
[discord.py](https://github.com/Rapptz/discord.py) for the \
[Esolang Discord Server](https://discord.gg/vwsaeee).
'''

AUTHOR = 'LyricLy'
AUTHOR_LINK = f'https://github.com/{AUTHOR}'
GITHUB_LINK = f'{AUTHOR_LINK}/{NAME}'
