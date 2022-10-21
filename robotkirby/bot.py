import hikari
import tanjun
import os
from robotkirby.db.db_driver import Database


def build_bot() -> hikari.GatewayBot:
    token = os.environ.get('DISCORD_TOKEN')
    bot = hikari.GatewayBot(token)

    make_client(bot)

    return bot


def make_client(bot: hikari.GatewayBot) -> tanjun.Client:
    client = tanjun.Client.from_gateway_bot(
        bot,
        declare_global_commands=True
    )

    database = Database()

    client.set_type_dependency(Database, database)

    client.load_modules('robotkirby.plugins.utilities')
    client.load_modules('robotkirby.plugins.log_message')

    return client

