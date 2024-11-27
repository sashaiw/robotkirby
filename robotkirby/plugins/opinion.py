import hikari
import tanjun
import typing
from robotkirby.db.db_driver import Database
import numpy as np
from statistics import mean
from vaderSentiment import vaderSentiment

vaderSentiment.SPECIAL_CASES['based'] = 3

component = tanjun.Component()
sia = vaderSentiment.SentimentIntensityAnalyzer()

def score_to_text(score: float) -> str:
    ranges = {
        'an **extremely negative**': (-1.0, -0.8),
        'a **strongly negative**': (-0.8, -0.6),
        'a **moderately negative**': (-0.6, -0.4),
        'a **somewhat negative**': (-0.4, -0.2),
        'a **slightly negative**': (-0.2, -0.05),
        'a **neutral**': (-0.05, 0.05),
        'a **slightly positive**': (0.05, 0.2),
        'a **somewhat positive**': (0.2, 0.4),
        'a **moderately positive**': (0.4, 0.6),
        'a **strongly positive**': (0.6, 0.8),
        'an **extremely positive**': (0.8, 1.0),
    }

    for name, r in ranges.items():
        if r[0] <= score <= r[1]:
            return name

@component.with_slash_command
@tanjun.with_str_slash_option('topic', 'topic to check sentiment on')
@tanjun.with_member_slash_option('member', 'user to check sentiment on', default=None)
@tanjun.with_channel_slash_option('channel', 'channel to check sentiment on', default=None)
@tanjun.as_slash_command('opinion', 'Find out what a member/channel/server thinks of a topic')
async def opinion(
        ctx: tanjun.abc.Context,
        topic: str,
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

    await ctx.respond(f"Trying to figure out what {prefix_str} thinks about {topic}...")

    messages = db.get_messages(
        member=member,
        guild=ctx.guild_id,
        channel=channel,
        text=topic
    )

    if messages is not None and len(messages) > 0:
        scores = np.array([sia.polarity_scores(m) for m in messages])

        compound = np.asarray([s['compound'] for s in scores])
        neu = np.asarray([s['neu'] for s in scores])

        # weight neutral scores less, opinionated scores more
        try:
            score = np.average(compound, weights=1-neu)
        except ZeroDivisionError:
            score = np.average(compound)

        await ctx.edit_initial_response(f"{prefix_str} has {score_to_text(score)} opinion of *{topic}*.\n"
                                        f"`score={score:.4f}`")
    else:
        await ctx.edit_initial_response(f"{prefix_str} doesn't have an opinion on *{topic}*")


@tanjun.as_loader
def load(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
