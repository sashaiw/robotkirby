import tanjun
from robotkirby.db.db_driver import Database

component = tanjun.Component()


@component.with_slash_command
@tanjun.as_slash_command('delete', 'Delete all of your own data.', default_to_ephemeral=True)
async def delete(
        ctx: tanjun.abc.Context,
        db: Database = tanjun.inject(type=Database)
) -> None:
    count = db.delete_by_user(ctx.author)
    await ctx.respond(f'{count} messages deleted.')


@tanjun.as_loader
def load(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
