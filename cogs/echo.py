import discord
from discord.ext import commands
from cogs.utils import checks

class Echo:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def echo(self, echo : str):
        await self.bot.say(echo)


def setup(bot):
    bot.add_cog(Echo(bot))
