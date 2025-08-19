from robotkirby.bot import build_bot

# if os.name != "nt":
#     import uvloop
#     uvloop.install()


def main():
    bot = build_bot()
    bot.run()


if __name__ == "__main__":
    main()
