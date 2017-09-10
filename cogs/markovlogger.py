import filehandler as fh


class Markovlogger:
    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        blacklist = ("171290851232710657","171413531915190272","240522682125254656")
        prefixes = ("!", "-", "~")
        if message.author.id not in blacklist and not message.content.startswith(prefixes):
            fh.write("markov", message.author.id, message.content)


def setup(bot):
    bot.add_cog(Markovlogger(bot))
