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
        await ctx.respond(sentence)
    else:
        await ctx.respond("I don't have enough data for this filter.")


@tanjun.as_loader
def load(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
