import discord
from discord.ext import commands



class Invite:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description = "Get invite link")
    async def invite(self):
        await self.bot.say("```https://discordapp.com/oauth2/authorize?client_id=171290386046779392&scope=bot&permissions=2146958591```")

def setup(bot):
    bot.add_cog(Invite(bot))
