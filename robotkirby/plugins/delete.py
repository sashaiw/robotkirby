import hikari
import tanjun
from robotkirby.db.db_driver import Database

component = tanjun.Component()

top_group = component.with_slash_command(tanjun.slash_command_group('delete', 'Delete your own data'))


@top_group.with_command
@tanjun.as_slash_command('all', 'delete all of your data from all servers', default_to_ephemeral=True)
async def delete_all(
        ctx: tanjun.abc.Context,
        db: Database = tanjun.inject(type=Database)
) -> None:
    count = db.delete_many(member=ctx.author)
    await ctx.respond(f'{count} messages deleted.')


@top_group.with_command
@tanjun.as_slash_command('server', 'delete all of your data from this server', default_to_ephemeral=True)
async def delete_server(
        ctx: tanjun.abc.Context,
        db: Database = tanjun.inject(type=Database)
) -> None:
    count = db.delete_many(member=ctx.author, guild=ctx.guild_id)
    await ctx.respond(f'{count} messages deleted.')


@top_group.with_command
@tanjun.with_channel_slash_option('channel', 'channel to delete your data from')
@tanjun.as_slash_command('channel', 'delete all of your data from a channel', default_to_ephemeral=True)
async def delete_channel(
        ctx: tanjun.abc.Context,
        channel: hikari.InteractionChannel,
        db: Database = tanjun.inject(type=Database),
) -> None:
    count = db.delete_many(member=ctx.author, guild=ctx.guild_id, channel=channel)
    await ctx.respond(f'{count} messages deleted.')


@tanjun.as_loader
def load(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
