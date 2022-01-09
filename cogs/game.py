import asyncio
import datetime
import random
import os
import re
import shutil
import uuid
from collections import defaultdict

import requests
import pygments
import pygments.lexers
import pygments.util
import discord
from discord.ext import commands

from utils import make_embed, load_json, save_json, Prompt, aggressive_normalize, get_pronouns
from constants.paths import CODE_GUESSING_SAVES, IDEA_SAVES


ip = requests.get("https://api.ipify.org").text
domain = f"http://{ip}:7001"


def filename_of_submission(sub, roundnum):
    if sub['language']:
        return f"./config/code_guessing/{roundnum}/{sub['uuid']}.{sub['language']}:{sub['filename']}"
    else:
        return f"./config/code_guessing/{roundnum}/{sub['uuid']}:{sub['filename']}"

def is_idea_message(content):
    return bool(re.match(r".*\bidea\s*:", content))


class OkButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.success, label="Approve")

    async def callback(self, interaction):
        self.view.s["tested"] = True
        save_json(CODE_GUESSING_SAVES, self.view.cg)
        await interaction.message.delete()

class ReportProblemButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.primary, label="Report problem")

    async def callback(self, interaction):
        await interaction.response.send_message("Provide a description of the problem to give to the author.", ephemeral=True)
        msg = await self.view.bot.wait_for("message", check=lambda m: not m.author.bot and m.channel.id == interaction.channel.id)
        await self.view.bot.get_user(int(self.view.s['id'])).send(f"A problem with your solution was reported:\n\n{msg.content}")
        await interaction.channel.send("Sent.")

class DismissButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.danger, label="Remove")

    async def callback(self, interaction):
        self.view.cg["round"]["submissions"].pop(self.view.s['id'])
        save_json(CODE_GUESSING_SAVES, self.view.cg)
        await interaction.message.delete()


class TestView(discord.ui.View):
    def __init__(self, bot, cg, s):
        super().__init__(timeout=None)
        self.bot = bot
        self.cg = cg
        self.s = s
        self.add_item(OkButton())
        self.add_item(ReportProblemButton())
        self.add_item(DismissButton())


class Games(commands.Cog):
    """Games! Fun and games! Have fun!"""

    def __init__(self, bot):
        self.bot = bot
        self.words = None
        self.cg = load_json(CODE_GUESSING_SAVES)
        self.ideas = load_json(IDEA_SAVES)

    @commands.Cog.listener("on_message")
    async def on_message_idea(self, message):
        if not message.author.bot and message.guild and is_idea_message(message.content):
            self.ideas.append({"guild_id": message.guild.id, "channel_id": message.channel.id, "message_id": message.id})
            save_json(IDEA_SAVES, self.ideas)

    @commands.command()
    async def idea(self, ctx):
        while True:
            i = random.randrange(len(self.ideas))
            m = self.ideas[i]
            try:
                msg = await self.bot.get_guild(m["guild_id"]).get_channel(m["channel_id"]).fetch_message(m["message_id"])
            except discord.HTTPException:
                self.ideas.pop(i)
                continue
            idea = msg.content
            if not is_idea_message(idea):
                self.ideas.pop(i)
                continue
            if idea.endswith("idea:"):
                idea_extra = await msg.channel.history(after=msg, check=lambda m: m.author == msg.author, limit=1).flatten()
                idea += "\n"
                idea += idea_extra[0].content
            await ctx.send(f"{msg.jump_url}\n{msg.content}", allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=False))
            break


    @commands.group(invoke_without_command=True)
    async def hwdyk(self, ctx):
        pass

    @hwdyk.command(aliases=["msg"])
    async def message(self, ctx):
        """Pick a random message. If you can guess who sent it, you win!"""

        # hardcoded list of "discussion" channels: esolang*, recreation-room, off-topic, programming, *-games
        channel = self.bot.get_channel(random.choice([
            348671457808613388,
            348702485994668033,
            348702065062838273,
            351171126594109455,
            348702212110680064,
            412764872816852994,
            415981720286789634,
            445375649511768074,
            348697452712427522
        ]))

        # this doesn't uniformly pick a random message: it strongly prefers messages sent after longer pauses, however this is a trade-off for an incredibly cheap getting oper-
        # ation which doesn't require spamming calls or storing data
        base = datetime.datetime(year=2020, month=1, day=1)
        while True:
            t = base + datetime.timedelta(milliseconds=random.randint(0, int((datetime.datetime.utcnow() - base).total_seconds() * 1000)))
            try:
                message = (await channel.history(after=t, limit=1).flatten())[0]
            except IndexError:
                pass
            else:
                if (not message.content or len(message.content) > 25) and message.author in ctx.guild.members:
                    break

        embed = make_embed(
            description=message.content,
            footer_text="#??? • ??/??/????",
        )
        embed.set_author(name="❓  ???")
        if message.attachments:
            filename = message.attachments[0].filename
            if filename.endswith(".png") or filename.endswith(".jpg") or filename.endswith(".jpeg"):
                embed.set_image(url=message.attachments[0].url)

        bot_msg = await ctx.send("Who sent this message?", embed=embed)

        while True:
            r = await self.bot.wait_for("message", check=lambda m: m.channel == ctx.channel and m.author == ctx.author)
            try:
                member = await commands.MemberConverter().convert(ctx, r.content)
            except commands.BadArgument:
                pass
            else:
                break

        # reveal info
        embed.set_footer(text="#" + message.channel.name)
        embed.timestamp = message.edited_at or message.created_at
        embed.set_author(name=message.author.name, icon_url=message.author.display_avatar)
        await bot_msg.edit(embed=embed)

        if member == message.author:
            await ctx.send("You were correct!")
        else:
            await ctx.send("Too bad. Good luck with the next time!")

    @commands.command(aliases=["tr", "type", "race"])
    @commands.guild_only()
    async def typerace(self, ctx, words: int = 10):
        """Race typing speeds!"""
        if not 5 <= words <= 50:
            return await ctx.send("Use between 5 and 50 words.")
        if not self.words:
            async with self.bot.session.get("https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english-usa-no-swears-medium.txt") as resp:
                self.words = (await resp.text()).splitlines()

        WAIT_SECONDS = 5
        await ctx.send(f"Type race begins in {WAIT_SECONDS} seconds. Get ready!")
        await asyncio.sleep(WAIT_SECONDS)

        prompt = " ".join(random.choices(self.words, k=words))
        zwsp = "\u2060"

        start = await ctx.send(zwsp.join(list(prompt.translate(str.maketrans({
            "a": "а",
            "c": "с",
            "e": "е",
            "s": "ѕ",
            "i": "і",
            "j": "ј",
            "o": "о",
            "p": "р",
            "y": "у",
            "x": "х"
        })))))

        winners = {}
        is_ended = asyncio.Event()
        timeout = False
        while not is_ended.is_set():
            done, pending = await asyncio.wait([
                self.bot.wait_for("message", check=lambda m: m.channel == ctx.channel and m.content.lower() == prompt.lower() and not m.author.bot and m.author not in winners),
                is_ended.wait()
            ], return_when=asyncio.FIRST_COMPLETED); [*map(asyncio.Task.cancel, pending)]
            r = done.pop().result()
            if isinstance(r, discord.Message):
                msg = r
            else:
                break
            await msg.delete()
            winners[msg.author] = (msg.created_at - start.created_at).total_seconds()
            if not timeout:
                timeout = True
                async def ender():
                    await asyncio.sleep(10)
                    is_ended.set()
                await ctx.send(f"{msg.author.name.replace('@', '@' + zwsp)} wins. Other participants have 10 seconds to finish.")
                self.bot.loop.create_task(ender())
        await ctx.send("\n".join(f"{i + 1}. {u.name.replace('@', '@' + zwsp)} - {t:.4f} seconds ({len(prompt) / t * 12:.2f}WPM)" for i, (u, t) in enumerate(winners.items())))


    def get_user_name(self, user_id):
        user_id = int(user_id)
        return "-".join((self.bot.get_user(user_id).name.lower() if user_id != self.cg["kit"] else "kit").split())

    @commands.group(invoke_without_command=True, aliases=["cg", "codeguessing"])
    async def codeguess(self, ctx):
        if "round" not in self.cg:
            return await ctx.send("There isn't a game of code guessing running here at the moment. Check in later?")
        d = self.cg["round"]

        if d["stage"] == 1:
            await ctx.send("The current round is in stage 1 (writing) right now, meaning anyone can participate. Check <#746231084353847366> for more information on what the challenge is for this round. "
                           "To submit an entry, just DM me your program as an attachment. Note that the filename **will not** be secret.")
        elif d["stage"] == 2 and str(ctx.author.id) not in d["submissions"]:
            await ctx.send("The current round is in stage 2 (guessing) right now, and only people who submitted solutions during stage 1 are able to participate. "
                           "You didn't do anything last round, so there's nothing I can do for you. Come back next round.")
        else:
            assert d["stage"] == 2
            await ctx.send(embed=discord.Embed(description=f"The current round is in stage 2 (guessing). Look at the list of submissions and try to figure out who wrote what. "
                                                            "Once you're done, submit your guesses like this (it should be a bijection from entry to user):\n"
                                                            "```\n1: lyricly\n2: christina\n3: i-have-no-other-names\n```"))

    @commands.has_role("Event Managers")
    @codeguess.command()
    async def kit(self, ctx, member: discord.Member):
        self.cg["kit"] = member.id
        p = get_pronouns(member)
        await ctx.send(f"{member.display_name} assigned as the stand-in for Kit. {p.pos_det.title()} name will be replaced with Kit's accordingly.")

    @commands.has_role("Event Managers")
    @codeguess.command()
    async def start(self, ctx, round_num: int):
        await ctx.message.delete()
        if "round" in self.cg:
            return await ctx.send("There's already a game running, though?", delete_after=2)
        shutil.rmtree(f"./config/code_guessing/{round_num}", ignore_errors=True)
        self.cg["round"] = {"round": round_num, "stage": 1, "submissions": {}, "guesses": {}}
        save_json(CODE_GUESSING_SAVES, self.cg)
        await ctx.send("All right! Keep in mind that to submit your entry, you just have to DM me the program as an attachment (the filename **will not** be secret) and I'll do the rest. "
                       "Good luck and have fun.")

    async def take_submission(self, message):
        d = self.cg["round"]
        attachment = message.attachments[0]

        code = await attachment.read()
        try:
            code_str = code.decode("utf-8")
        except UnicodeDecodeError:
            code_str = None

        try:
            guess = pygments.lexers.get_lexer_for_filename(attachment.filename)
        except (pygments.util.ClassNotFound, KeyError):
            if code_str:
                try:
                    guess = pygments.lexers.guess_lexer(code_str)
                except (pygments.util.ClassNotFound, KeyError):
                    guess = None
            else:
                guess = None

        choices = ["Java", "C#", "PHP", "Python", "JavaScript", "WASM", "It's complicated"]
        p = Prompt(message.author)
        if guess and guess.name in choices:
            choices.remove(guess.name)
            p.add_option(guess.name, discord.ButtonStyle.primary)
        for choice in choices:
            p.add_option(choice, discord.ButtonStyle.secondary)

        await message.channel.send("What language is this written in?", view=p)
        lang = await p.response()
        shortname = {
            "JavaScript": "js",
            "C": "c",
            "Bash": "sh",
            "Brainfuck": "bf",
            "Rust": "rs",
            "Python": "py",
            "PHP": "php",
            "C#": "cs",
            "Java": "java",
            "WASM": None,
            "It's complicated": None,
        }[lang]
        i = str(message.author.id)
        sub = {"id": i, "filename": attachment.filename, "tested": False, "language": shortname, "uuid": str(uuid.uuid4())}
        if i in d["submissions"]:
            os.remove(filename_of_submission(d["submissions"][i], d["round"]))
        d["submissions"][i] = sub
        save_json(CODE_GUESSING_SAVES, self.cg)

        filename = filename_of_submission(sub, d["round"])
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "wb") as f:
            f.write(code)

        if code_str is None:
            await message.channel.send("I successfully submitted your entry, but I noticed that the file isn't encoded in valid UTF-8. "
                                       "That could cause issues or something, so maybe don't do that. Your call, though. I'm just letting you know. "
                                       "You'll be informed of any problems found while testing. Just resubmit if there are any issues. "
                                       "If you need to talk anonymously to the event managers, send an anonymous message with `!anon LyricLy`.")
        else:
            await message.channel.send("Successfully submitted your entry. You'll be informed of any problems found while testing. Just resubmit if there are any issues. "
                                       "If you need to talk anonymously to the event managers, send an anonymous message with `!anon LyricLy`.")

    async def take_guesses(self, message):
        d = self.cg["round"]
        guess = {}
        guessed_people = set()
        submissions = list(filter(None, d["submissions"].values()))
        submissions.sort(key=lambda e: filename_of_submission(e, d["round"]))

        for line in message.content.strip("`").splitlines():
            if not line.strip():
                continue

            if ":" not in line:
                return await message.channel.send(f"Invalid line `{line}` found during parsing. All lines must be of the form `#<num>: <name>`. Aborting.")
            index_s, user_s = line.split(":")

            try:
                index = int(index_s.strip().lstrip("#"))
            except ValueError:
                return await message.channel.send(f"Invalid index '{index_s}' found while parsing guess. Aborting.")

            user = discord.utils.find(
                lambda us: aggressive_normalize(user_s) in map(aggressive_normalize, filter(None, (self.get_user_name(int(us)), us))),
                d["submissions"],
            )
            if user is None:
                return await message.channel.send(f"Unknown user '{user_s}'. Aborting.")

            if index == 0:
                return await message.channel.send("Index 0 is out of bounds. These are 1-indexed. Aborting.")
            elif index < 0:
                return await message.channel.send("Negative indices are inappropriate. Aborting.")
            elif index > len(d["submissions"]):
                return await message.channel.send(f"Index {index} is out of bounds as there are only {len(d['submissions'])} submissions. Aborting.")

            submission_id = submissions[index-1]['id']
            if submission_id in guess:
                return await message.channel.send(f"Duplicate guess for {index} found. Guesses are bijections. This is terrible. Aborting.")
            if user in guessed_people:
                return await message.channel.send(f"Duplicate guess for {user_s} found. Guesses are bijections. This is terrible. Aborting.")

            if user == submission_id == str(message.author.id):
                continue
            elif str(message.author.id) == user:
                return await message.channel.send("You guessed yourself for the wrong submission, dummy. Aborting, I guess?")
            elif str(message.author.id) == submission_id:
                return await message.channel.send("How did you guess your own solution wrong? Aborting for your own good.")

            guess[submission_id] = user
            guessed_people.add(user)

        if not guess:
            return

        d["guesses"][str(message.author.id)] = guess
        save_json(CODE_GUESSING_SAVES, self.cg)

        if len(guess) != len(d["submissions"])-1:
            await message.channel.send(f"I registered your guess, but I noticed that you haven't put in a guess for every entry (you guessed {len(guess)}, but there are {len(d['submissions'])}). "
                                       "This is allowed, but there's no reason to do it, as there's no penalty for guessing wrong. Consider putting in a few extra random guesses to maybe score "
                                       "some extra points! Just as with your code submission, you can re-submit your guesses at any time.")
        else:
            await message.channel.send("Guess registered. Have a swell day. Just as with your code submission, you can re-submit your guesses at any time.")

    @commands.Cog.listener("on_message")
    async def on_message_cg(self, message):
        if message.author.bot or message.guild or "round" not in self.cg:
            return
        if self.cg["round"]["stage"] == 1 and len(message.attachments) == 1:
            await self.take_submission(message)
        elif self.cg["round"]["stage"] == 2 and str(message.author.id) in self.cg["round"]["submissions"] and not message.content.startswith("!"):
            await self.take_guesses(message)

    @commands.has_role("Event Managers")
    @codeguess.command()
    async def test(self, ctx):
        if "round" not in self.cg:
            return await ctx.send("There's no game running.")
        d = self.cg["round"]
        if d["stage"] == 2:
            return await ctx.send("We're already in round 2, though...?")
        for i, s in d["submissions"].items():
            if not s["tested"]:
                await ctx.author.send(file=discord.File(filename_of_submission(s, d["round"]), s["filename"]), view=TestView(self.bot, self.cg, s))

    @commands.has_role("Event Managers")
    @codeguess.command(aliases=["r2", "next"])
    async def round2(self, ctx):
        await ctx.message.delete()
        if "round" not in self.cg:
            return await ctx.send("There's no game running. Did you mean to do `!cg start`?", delete_after=2)
        d = self.cg["round"]
        if d["stage"] == 2:
            return await ctx.send("We're already in round 2. Did you mean to do `!cg stop`?", delete_after=2)
        if not all(s["tested"] for s in d["submissions"].values()):
            return await ctx.send("Easy there. There are untested submissions to attend to. Deal with them using `!cg test` first.", delete_after=2)

        with open(f"./config/code_guessing/{d['round']}/people", "w") as f:
            f.write("\n".join(self.get_user_name(int(i)) for i in sorted(d["submissions"])))

        d["stage"] = 2
        save_json(CODE_GUESSING_SAVES, self.cg)
        await ctx.send(embed=discord.Embed(description=f"You can no longer send submissions, and the guessing phase has begun. "
                                                        "For more on how to guess, do `!cg` in <#457999277311131649>."))

    @commands.has_role("Event Managers")
    @codeguess.command(aliases=["end"])
    async def stop(self, ctx):
        await ctx.message.delete()
        if "round" not in self.cg:
            return await ctx.send("Can't stop what isn't running.", delete_after=2)
        d = self.cg["round"]
        if d["stage"] == 1:
            self.cg.pop("round")
            save_json(CODE_GUESSING_SAVES, self.cg)
            return await ctx.send("Bit premature to be stopping, no? Well, in any case, I've done as you asked. No results file generated, because the round wasn't done.")

        good = defaultdict(int)
        bad = defaultdict(int)

        with open(f"./config/code_guessing/{d['round']}/results.txt", "w+") as f:
            submissions = list(d["submissions"].values())
            submissions.sort(key=lambda e: filename_of_submission(e, d["round"]))

            f.write("correct answers:\n")
            for idx, user in enumerate(submissions, start=1):
                f.write(f"#{idx}: {self.get_user_name(user['id'])}\n")

            f.write("\n\npeople's guesses:\n")
            for user, guess in d["guesses"].items():
                f.write(f"\n{self.get_user_name(user)} guessed:\n")
                for idx, s in enumerate(submissions, start=1):
                    actual = s["id"]
                    guessed = guess.get(actual)
                    if not guessed:
                        continue
                    if actual == guessed:
                        f.write(f"[O] #{idx} correctly as {self.get_user_name(actual)}\n")
                        good[user] += 1
                        bad[actual] += 1
                    else:
                        f.write(f"[X] #{idx} incorrectly as {self.get_user_name(guessed)} (was {self.get_user_name(actual)})\n")

            f.write("\n\nscores this round:\n")
            for user in sorted(d["submissions"], key=lambda u: good[u] - bad[u], reverse=True):
                f.write(f"{self.get_user_name(user)} +{good[user]} -{bad[user]} = {good[user] - bad[user]}\n")

            f.seek(0)
            self.cg.pop("round")
            save_json(CODE_GUESSING_SAVES, self.cg)
            await ctx.send("Game's over! Results can be found in the attached file or on the website.", file=discord.File(f, "results.txt"))


def setup(bot):
    bot.add_cog(Games(bot))
