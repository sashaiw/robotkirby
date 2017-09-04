import discord
import random
import time
import re
import os
import filehandler as fh
import codecs
import multiprocessing as mp
from discord.ext import commands
import markovify
from cogs.utils import checks



class Sentient:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context = True, description = "Uses Markov chains to emulate users. Pass mention as arg.")
    @checks.is_licensed()
    async def sentient(self, ctx, arg : str):
        if arg == "hivemind":
            await self.bot.say("Hivemind is borked. :c")
#            start = time.time()
#            tries = 100
#            models = []
#            dirs = os.listdir("db/markov/")
#            dirsize = os.path.getsize("db/markov")
#            await self.bot.say("`Loading database for " + str(len(dirs)) + " users ("+str(dirsize/100)+" kB)...`")
#            await self.bot.send_typing(ctx.message.channel)
#            for i in dirs:
#                with codecs.open("db/markov/" + i, "r", encoding="utf-8",errors="ignore") as f:
#                    text = f.read()
#                models.append(markovify.NewlineText(text))
#            await self.bot.say("`Combining data...`")
#            await self.bot.send_typing(ctx.message.channel)
#            model = markovify.combine(models)
#            await self.bot.say("`Attempting to generate sentence (best of "+str(tries)+" attempts)...`")
#            await self.bot.send_typing(ctx.message.channel)
#            sentence = model.make_sentence(tries=tries)
#            end = time.time()
#            await self.bot.say("`Done. Took "+str(round(end-start))+"s`")
#            if sentence is None:
#                await self.bot.say("`INSUFFICIENT DATA`")
#            else:
#                sentence = re.sub("<@!?[0-9]{16,32}>|@everyone", "", sentence)
#                await self.bot.say(sentence)
        else:
            try:
                mentionid = ctx.message.mentions[0].id
            except IndexError:
                mentionid = arg
            try:
                with open("db/markov/" + mentionid + ".txt") as f:
                    text = f.read()
            except FileNotFoundError:
                text = ""

            model = markovify.NewlineText(text)
            sentence = model.make_sentence(tries=100)
            if sentence is None:
                await self.bot.say("`INSUFFICIENT DATA`")
            else:
                sentence = re.sub("<@!?[0-9]{16,32}>|@everyone", "", sentence)
                await self.bot.say(sentence)

def setup(bot):
    bot.add_cog(Sentient(bot))
