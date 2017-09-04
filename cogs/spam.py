import discord
import random
import filehandler as fh
from discord.ext import commands
from cogs.utils import checks


class Spam:
    def __init__(self, bot):
        self.bot = bot

    voice = {}
    micspamming = {}
    micspam = {}

    @commands.group(pass_context=True, description = "Micspams links from Youtube or Soundcloud.")
    @checks.is_licensed()
    async def spam(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.say("```See !help spam.```")

    @checks.is_chron()
    @spam.command(name='cstart', pass_context=True, description="This command does not exist.")
    async def _cstart(self, ctx, channel : str, link : str):
        server = self.bot.get_channel(channel).server.id
        spamsites = ("https://www.youtube.com/watch?v=","http://youtu.be/","https://soundcloud.com/", "http://www.pornhub.com/view_video.php?viewkey=")
        if link.startswith(spamsites):
            if server not in self.micspamming:
                self.micspamming[server] = False
            if self.micspamming[server]:
                self.micspam[server].stop()
                self.micspamming[server] = False
            if not self.bot.is_voice_connected(self.bot.get_channel(channel).server):
                self.voice[server] = await self.bot.join_voice_channel(self.bot.get_channel(channel))
                self.micspamming[server] = False
            else:
                await self.voice[server].move_to(self.bot.get_channel(channel))
                self.micspamming[server] = False
            self.micspam[server] = await self.voice[server].create_ytdl_player(link)
            self.micspam[server].start()
            self.micspamming[server] = True
            response = random.choice(fh.read("all","musicresponses")).rstrip("\n")

    @spam.command(name='start', pass_context=True, description = "Starts spam. Pass link as argument. You need to be in a voice channel.")
    async def _start(self, ctx, link : str):
        spamsites = ("https://www.youtube.com/watch?v=","http://youtu.be/","https://soundcloud.com/", "http://www.pornhub.com/view_video.php?viewkey=")
        if link.startswith(spamsites):
            if ctx.message.server.id not in self.micspamming:
                self.micspamming[ctx.message.server.id] = False
            if ctx.message.author.voice_channel:
                if self.micspamming[ctx.message.server.id]:
                    self.micspam[ctx.message.server.id].stop()
                    self.micspamming[ctx.message.server.id] = False
                if not self.bot.is_voice_connected(ctx.message.server):
                    self.voice[ctx.message.server.id] = await self.bot.join_voice_channel(ctx.message.author.voice_channel)
                    self.micspamming[ctx.message.server.id] = False
                else:
                    await self.voice[ctx.message.server.id].move_to(ctx.message.author.voice_channel)
                    self.micspamming[ctx.message.server.id] = False
                self.micspam[ctx.message.server.id] = await self.voice[ctx.message.server.id].create_ytdl_player(link)
                self.micspam[ctx.message.server.id].start()
                self.micspamming[ctx.message.server.id] = True
                response = random.choice(fh.read("all","musicresponses")).rstrip("\n")
                response += '\n```       Title: ' + self.micspam[ctx.message.server.id].title
                response += '\n         URL: ' + self.micspam[ctx.message.server.id].url
                response += '\nRequested by: ' + ctx.message.author.name + '#' + str(ctx.message.author.discriminator) + '```'
                await self.bot.say(response)
            else:
                await self.bot.say("Hey, you aren't in a voice channel. Join one so I know what channel to join. Thanks!")

    @spam.command(name='stop', pass_context=True, description = "Stops currently playing spam.")
    async def _stop(self, ctx):
        self.micspam[ctx.message.server.id].stop()
        self.micspamming[ctx.message.server.id] = False

def setup(bot):
    bot.add_cog(Spam(bot))
