import tanjun
from robotkirby.db.db_driver import Database

component = tanjun.Component()

top_group = component.with_slash_command(tanjun.slash_command_group('opt', 'Opt in or out'))


@top_group.with_command
@tanjun.as_slash_command('in', 'opt in', default_to_ephemeral=True)
async def optin(
        ctx: tanjun.abc.Context,
        db: Database = tanjun.inject(type=Database)
) -> None:
    db.update_permissions(member=ctx.author, read_messages=True)
    await ctx.respond(f'You have successfully opted in to data collection.')


@top_group.with_command
@tanjun.as_slash_command('out', 'opt out', default_to_ephemeral=True)
async def optout(
        ctx: tanjun.abc.Context,
        db: Database = tanjun.inject(type=Database)
) -> None:
    db.update_permissions(member=ctx.author, read_messages=False)
    await ctx.respond(f'You have successfully opted out of data collection.')


@tanjun.as_loader
def load(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
