import discord
import random
import re
import filehandler as fh
from discord.ext import commands
from cogs.utils import checks



class Meme:
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True, description = "[LICENSE NECCESARY] Displays meme. See !help meme for more info.")
    @checks.is_licensed()
    async def meme(self, ctx):
        if ctx.invoked_subcommand is None:
            try:
                self.meme = random.choice(fh.read(ctx.message.server.id,"memes")).rstrip("\n")
                await self.bot.say(self.meme)
            except TypeError:
                await self.bot.say("Looks like I don't have any memes on file for your server. You can add memes with !meme add as long as you are a licensed memer.")

    @meme.command(name='add', pass_context=True, description = "Adds imgur link to meme database. Pass link as argument.")
    async def _add(self, ctx, link : str):
        link = re.match("https?://i?.?imgur.com/([a-zA-Z0-9]{5,7}.(jpg|png|gif|webm))", link)
        if link:
            link = "http://i.imgur.com/" + link.group(1)
            if fh.write(ctx.message.server.id,"memes", link):
                msg = "Thank you very much. There are now " + str(len(fh.read(ctx.message.server.id,"memes"))) + " memes in the meme database."
                await self.bot.say(msg)
            else:
                await self.bot.say("Looks like this meme is already in my database. Thanks anyway!")
        else:
            await self.bot.say("Dude, that's not a valid link.")

    @commands.command(name='approve', pass_context = True, description = "Approves a meme license. Admin required.")
    @checks.is_admin()
    async def _approve(self, ctx, user : str):
        try:
            mentionid = ctx.message.mentions[0].id
        except IndexError:
            mentionid = arg
        if fh.write(ctx.message.server.id,"licenses",mentionid):
            await self.bot.say("`Adding user with ID: " + mentionid + "`")
        else:
            await self.bot.say("`A user already exists with id: " + mentionid + "`")

    @commands.command(name='revoke', pass_context = True, description = "Revokes a meme license. Admin required.")
    @checks.is_admin()
    async def _revoke(self, ctx, user : str):
        try:
            mentionid = ctx.message.mentions[0].id
        except IndexError:
            mentionid = arg
        if fh.remove(ctx.message.server.id,"licenses",mentionid):
            await self.bot.say("`Removing user with ID: " + mentionid + "`")
        else:
            await self.bot.say("`No user with id: " + mentionid + "`")

    @meme.command(name='remove', pass_context = True, description = "Removes a meme. Admin required.")
    @checks.is_admin()
    async def _remove(self, ctx, link : str):
        fh.remove(ctx.message.server.id,"memes",link)
        await self.bot.say("`Removing meme.`")

def setup(bot):
    bot.add_cog(Meme(bot))
