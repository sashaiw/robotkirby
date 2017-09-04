import discord
import random
import asyncio
import filehandler as fh
from discord.ext import commands
from cogs.utils import checks



class Tribal:
    def __init__(self, bot):
        self.bot = bot

    users = {}
    voted = []

    async def on_ready(self):
        channel = self.bot.get_channel("160181529522339841")
        while True:
            minutes = 15
            self.users={}
            self.voted=[]
            for i in range(1,minutes):
                message = "```VOTES:\n"
                if self.users:
                    for user in self.users:
                        message = message + user.name + ": " + str(self.users[user]) + "\n"
                else:
                    message = message + "NO VOTES. WILL BAN RANDOM USER!\n"
                message = message + str(minutes - i) + " minutes remaining.```"
                await self.bot.send_message(channel, message)
                await asyncio.sleep(60)
            if self.users:
                maxvotes = (0, 0)
                for user in list(self.users):
                    if self.users[user] > maxvotes[1]:
                        maxvotes = (user, self.users[user])
                await self.bot.send_message(channel, "Banning user: " + maxvotes[0].name)
                await self.bot.kick(maxvotes[0])
            else:
                maxvotes = random.choice(list(channel.server.members))
                await self.bot.send_message(channel, "No votes received. Banning: " + maxvotes.name)
                await self.bot.kick(maxvotes)

    @commands.command(name='vote', pass_context = True, description = "Vote for elimination.")
    async def _vote(self, ctx):
        try:
            user = ctx.message.mentions[0]
        except IndexError:
            await self.bot.say("```Syntax: !vote <@mention>```")
            return
        if user.id in ("89398547308380160", "171290851232710657"):
            await self.bot.say("This user is blacklisted.")
            return
        if ctx.message.author not in self.voted:
            self.voted.append(ctx.message.author)
            if user not in self.users:
                self.users[user] = 1
            else:
                self.users[user] += 1
            message = "```VOTES:\n"
            if self.users:
                for user in self.users:
                    message = message + user.name + ": " + str(self.users[user]) + "\n"

        else:
            await self.bot.say("You can't vote twice.")

    @commands.command(name="votes", pass_context=True, description="Show current votes")
    async def _votes(self, ctx):
        message = "```"
        for user in self.users:
            message = message + user.name + ": " + str(self.users[user]) + "\n"

        message = message + "```"
        await self.bot.say(message)


def setup(bot):
    bot.add_cog(Tribal(bot))
