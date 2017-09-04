import discord
import random
import asyncio
import filehandler as fh
from discord.ext import commands



class ARG:
    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        while True:
            await self.bot.change_presence(game=discord.Game(name=random.choice(fh.read("all", "games")).rstrip("\n")))
            await asyncio.sleep(3600)


def setup(bot):
    bot.add_cog(ARG(bot))
