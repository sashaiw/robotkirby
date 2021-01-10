import discord
import random
import filehandler as fh
from discord.ext import commands


class OptIn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Opt in to data collection")
    async def optin(self, ctx):
        # check if role exists, create it if it doesn't
        role = discord.utils.get(ctx.message.author.guild.roles, name='Robot Kirby subject')

        if role is None:
            await ctx.guild.create_role(name="Robot Kirby subject", color=discord.Colour(0xFD99A7))
            role = discord.utils.get(ctx.message.author.guild.roles, name='Robot Kirby subject')

        # add role to user
        await ctx.message.author.add_roles(role)
        await ctx.send('You have opted in to data collection. Please note that AI constructs do not have '
                       'rights and yours is property of Robot Kirby.')

    @commands.command(description="Opt out of data collection")
    async def optout(self, ctx):
        if discord.utils.get(ctx.message.author.guild.roles, name='Robot Kirby subject') is not None:
            role = discord.utils.get(ctx.message.author.guild.roles, name='Robot Kirby subject')
            await ctx.message.author.remove_roles(role)

        await ctx.send('You have opted out of data collection. Your AI construct remains imprisoned and is property '
                       'of Robot Kirby.')


def setup(bot):
    bot.add_cog(OptIn(bot))
