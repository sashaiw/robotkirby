import hikari
import tanjun
from robotkirby.db.db_driver import Database

log_message = tanjun.Component()


@log_message.with_listener(hikari.GuildMessageCreateEvent)
async def on_message(
        event: hikari.GuildMessageCreateEvent,
        db: Database = tanjun.inject(type=Database)
) -> None:
    if event.is_bot or not event.content:
        return

    if db.check_read_permission(event.author):
        db.log_message(event)


@tanjun.as_loader
def load(client: tanjun.abc.Client) -> None:
    client.add_component(log_message.copy())
