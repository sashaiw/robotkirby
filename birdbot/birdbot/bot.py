import hikari
import tanjun
import os
from birdbot.database import Database

def build_bot() -> hikari.GatewayBot:
    token = os.environ.get('DISCORD_TOKEN')
    print(f'TOKEN: {os.environ}')
    bot = hikari.GatewayBot(token)

    make_client(bot)

    return bot


def make_client(bot: hikari.GatewayBot) -> tanjun.Client:
    client = tanjun.Client.from_gateway_bot(
        bot,
    )

    db = Database()
    client.set_type_dependency(Database, db)

    client.load_modules('birdbot.modules.aggregator')

    return client