import hikari
from birdbot.bot import build_bot


# if os.name != "nt":
#     import uvloop
#     uvloop.install()

if __name__ == '__main__':
    bot = build_bot()
    bot.run()