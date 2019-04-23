from discord.ext import commands
import discord.utils
import filehandler as fh

def is_licensed_check(message):
    #return message.channel.is_private or message.author.id in fh.read(message.server.id,"licenses")
    return true

def is_licensed():
    return commands.check(lambda ctx: is_licensed_check(ctx.message))

def is_chron_check(message):
    return message.author.id in ("345410115563683841", "89398547308380160")

def is_chron():
    return commands.check(lambda ctx: is_chron_check(ctx.message))

def is_admin_check(message):
    return message.author.id in ("345410115563683841", "89398547308380160", "89412220898803712") or message.author.id == message.server.owner.id

def is_admin():
    return commands.check(lambda ctx: is_admin_check(ctx.message))
