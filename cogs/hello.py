import discord
import random
import filehandler as fh
from discord.ext import commands



class Hello:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description = "Say hi to Kirby")
    async def hello(self):
        im = random.choice(fh.read("all", "hello")).rstrip("\n")
        await self.bot.say(im)

def setup(bot):
    bot.add_cog(Hello(bot))
