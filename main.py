import discord
from discord.ext import commands
import logging
from cogs.utils import checks
import filehandler as fh

try:
    with open('token.txt', 'r') as tokenfile:
        token = tokenfile.read()
except FileNotFoundError:
    print('Please place your token in a file titled "token.txt"')

logger = logging.getLogger('kirby')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='kirby.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

description = '''<('.')> ROBOT KIRBY 2.0 BETA'''

startup_extensions = ["cogs.hello",
                      "cogs.insult",
                      "cogs.spam",
                      "cogs.meme",
                      "cogs.sentient",
                      "cogs.markovlogger",
                      "cogs.temp",
                      "cogs.arg",
                      "cogs.invite",
                      "cogs.giftcard",
                      "cogs.trumptweets"]

bot = commands.Bot(command_prefix='!', description=description)


@bot.event
async def on_ready():
    print("---[(>\")> Robot Kirby is now operational.]---")

if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

    bot.run(token)
