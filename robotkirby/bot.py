import os

import hikari
import tanjun

from robotkirby.db.db_driver import Database


def build_bot() -> hikari.GatewayBot:
    token = os.environ.get("DISCORD_TOKEN")
    intents = hikari.Intents.GUILD_MESSAGES | hikari.Intents.GUILD_MEMBERS
    if token is None:
        raise ValueError("DISCORD_TOKEN environment variable is not set")
    bot = hikari.GatewayBot(token, intents=intents)

    make_client(bot)

    return bot


def make_client(bot: hikari.GatewayBot) -> tanjun.Client:
    client = tanjun.Client.from_gateway_bot(
        bot,
        declare_global_commands=True,
        # declare_global_commands=1306815895829614687  # for testing lol (this is my server now sry) - amelia
    )

    database = Database()

    client.set_type_dependency(Database, database)

    client.load_modules("robotkirby.plugins.utilities")
    client.load_modules("robotkirby.plugins.log_message")
    client.load_modules("robotkirby.plugins.sentient")
    client.load_modules("robotkirby.plugins.optin")
    client.load_modules("robotkirby.plugins.delete")
    client.load_modules("robotkirby.plugins.wordcloud")
    client.load_modules("robotkirby.plugins.opinion")
    client.load_modules("robotkirby.plugins.timedensity")
    client.load_modules("robotkirby.plugins.rankedopinion")
    client.load_modules("robotkirby.plugins.similarity")
    # client.load_modules('robotkirby.plugins.wrapped')

    return client
