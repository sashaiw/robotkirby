import filehandler as fh
from discord.ext import commands
import discord


class Markovlogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        role = discord.utils.get(message.author.guild.roles, name='Robot Kirby subject')
        if message.author.roles is not None and role in message.author.roles:
            blacklist = ("171290851232710657", "171413531915190272", "240522682125254656")
            prefixes = ("!", "-", "~", "c!")
            if message.author.id not in blacklist and not message.content.startswith(prefixes):
                fh.write("markov", message.author.id, message.content)


def setup(bot):
    bot.add_cog(Markovlogger(bot))
