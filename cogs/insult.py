import discord
import random
import filehandler as fh
from discord.ext import commands



class Insult:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description = "Generates insult")
    async def insult(self):
        im = random.choice(fh.read("all", "insult")).rstrip("\n")
        await self.bot.say(im)

def setup(bot):
    bot.add_cog(Insult(bot))
