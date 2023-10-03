import hikari
import tanjun
import typing
from robotkirby.db.db_driver import Database
import markovify

component = tanjun.Component()


@component.with_slash_command
@tanjun.with_member_slash_option('member', 'user to imitate', default=None)
@tanjun.with_channel_slash_option('channel', 'channel to imitate', default=None)
@tanjun.as_slash_command('sentient', 'Imitate user')
async def sentient(
        ctx: tanjun.abc.Context,
        member: typing.Optional[hikari.Member],
        channel: typing.Optional[hikari.InteractionChannel],
        db: Database = tanjun.inject(type=Database)
) -> None:
    if not db.check_read_permission(ctx.author):
        await(ctx.respond('In order to use Robot Kirby, please opt in to data collection using the `/opt in` command. '
                          'This will allow me to collect your messages so that I can build sentences from your data. '
                          ':heart:'))
        return

    match (member, channel):
        case (None, None):
            prefix_str = f'**{ctx.get_guild().name}**'
        case (hikari.Member(), None):
            prefix_str = f'{member.mention}'
        case (None, hikari.InteractionChannel()):
            prefix_str = f'{channel.mention}'
        case (hikari.Member(), hikari.InteractionChannel()):
            prefix_str = f'{member.mention} in {channel.mention}'
        case _:
            await ctx.respond(f"Something is broken about this query.")
            return

    await ctx.respond(f"Thinking about {prefix_str}...")

    messages = db.get_messages(
        member=member,
        guild=ctx.guild_id,
        channel=channel
    )

    sentence = None
    if messages is not None and len(messages) > 0:
        model = markovify.Text(messages)
        sentence = model.make_sentence()

    if sentence is not None:
        await ctx.edit_initial_response(f"{prefix_str}:\n{sentence}")
    else:
        await ctx.edit_initial_response(f"I don't have enough data for {prefix_str}.")


@tanjun.as_loader
def load(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
