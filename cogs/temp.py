import discord
import random
import filehandler as fh
from discord.ext import commands
from cogs.utils import checks



class Temp:
    def __init__(self, bot):
        self.bot = bot

    channels = {}

    async def on_voice_state_update(self, before, after):
        if after.id in self.channels and before.voice.voice_channel != after.voice.voice_channel and after.voice.voice_channel != self.channels[after.id]:
            await self.bot.delete_channel(self.channels[after.id])
            self.channels[after.id] = None

    async def on_ready(self):
        tempchannels = fh.read("all","tempchannels")
        if tempchannels:
            for c in tempchannels:
                try:
                    await self.bot.delete_channel(self.bot.get_channel(c))
                except AttributeError:
                    pass
            fh.kill("all","tempchannels")

    @commands.group(pass_context=True, description = "Creates a temporary channel.")
    @checks.is_licensed()
    async def temp(self,ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.say("```See !help temp.```")

    @temp.command(name='create', pass_context=True, description="Creates a temporary channel")
    async def _create(self,ctx):
        if ctx.message.author.id not in self.channels or self.channels[ctx.message.author.id] is None:
            channelname = ctx.message.author.name + "\'s " + random.choice(fh.read("all","channelnames")).rstrip("\n")

            everyone = discord.PermissionOverwrite(connect=False)
            self.channels[ctx.message.author.id] = await self.bot.create_channel(ctx.message.server, channelname, (ctx.message.server.default_role, everyone), type=discord.ChannelType.voice)

            print(self.channels[ctx.message.author.id].id)
            fh.write("all","tempchannels",self.channels[ctx.message.author.id].id)
            await self.bot.move_member(ctx.message.author,self.channels[ctx.message.author.id])
            await self.bot.say("```Created channel with name \"" + channelname + "\"```")
        else:
            await self.bot.say("You already have a temp channel.")

    @temp.command(name='delete', pass_context=True, description="Deletes a temporary channel")
    async def _delete(self,ctx):
        if ctx.message.author.id in self.channels:
            if ctx.message.server.afk_channel:
                print("MOVING")
                for member in self.channels[ctx.message.author.id].voice_members:
                    await self.bot.move_member(member,ctx.message.server.afk_channel)
            fh.remove("all","tempchannels",self.channels[ctx.message.author.id].id)
            await self.bot.delete_channel(self.channels[ctx.message.author.id])
            del self.channels[ctx.message.author.id]
        else:
            await self.bot.say("You don't have a temp channel.")

    @temp.command(name="accept", pass_context=True, description="Accepts a user into temporary channel.")
    async def _accept(self, ctx, user : str):
        try:
            mentionid = ctx.message.mentions[0].id
        except IndexError:
            mentionid = arg

        member = ctx.message.server.get_member(mentionid)
        if ctx.message.author.id in self.channels:
            await self.bot.move_member(member,self.channels[ctx.message.author.id])

    @temp.command(name="purge", pass_context=True, description="Purges all temp channels. Admin required.")
    @checks.is_licensed()
    async def _purge(self,ctx):
        for c in fh.read("all","tempchannels"):
            try:
                await self.bot.delete_channel(self.bot.get_channel(c))
            except AttributeError:
                pass
        self.channels = {}
        fh.kill("all","tempchannels")

def setup(bot):
    bot.add_cog(Temp(bot))
