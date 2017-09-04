import discord
import random
import filehandler as fh
from discord.ext import commands

class Giftcard:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context = True, description = "Get gift card")
    async def giftcard(self, ctx):
        if ctx.message.author.id != "113383263724118016":
            chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
            msg = "`"
            for i in range(0,5):
                msg += random.choice(chars)
            msg += "-"
            for i in range(0,5):
                msg += random.choice(chars)
            msg += "-"
            for i in range(0,5):
                msg += random.choice(chars)
            msg += "`"
            await self.bot.say(msg)
        else:
            await self.bot.say("Sorry! We're all out of gift codes! Come back later!")

def setup(bot):
    bot.add_cog(Giftcard(bot))
