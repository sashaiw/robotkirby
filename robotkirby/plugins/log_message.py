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

    db.log_message(
        content=event.content,
        author=event.author_id,
        guild=event.guild_id
    )


@tanjun.as_loader
def load(client: tanjun.abc.Client) -> None:
    client.add_component(log_message.copy())
