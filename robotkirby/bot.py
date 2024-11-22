import hikari
import tanjun
import os
from robotkirby.db.db_driver import Database


def build_bot() -> hikari.GatewayBot:
    token = os.environ.get('DISCORD_TOKEN')
    bot = hikari.GatewayBot(token, intents=hikari.Intents.ALL)

    make_client(bot)

    return bot


def make_client(bot: hikari.GatewayBot) -> tanjun.Client:
    client = tanjun.Client.from_gateway_bot(
        bot,
        declare_global_commands=True
        # declare_global_commands=163475269422809089  # for testing lol
    )

    database = Database()

    client.set_type_dependency(Database, database)

    client.load_modules('robotkirby.plugins.utilities')
    client.load_modules('robotkirby.plugins.log_message')
    client.load_modules('robotkirby.plugins.sentient')
    client.load_modules('robotkirby.plugins.optin')
    client.load_modules('robotkirby.plugins.delete')
    client.load_modules('robotkirby.plugins.wordcloud')
    client.load_modules('robotkirby.plugins.opinion')
    client.load_modules('robotkirby.plugins.timedensity')
    # client.load_modules('robotkirby.plugins.wrapped')

    return client

