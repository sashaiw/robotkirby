import collections
import datetime
from dateutil.relativedelta import relativedelta
import operator
import typing

import hikari
import numpy as np
import tanjun
from vaderSentiment import vaderSentiment

from robotkirby.db.db_driver import Database
from opinion import score_to_text

vaderSentiment.SPECIAL_CASES['based'] = 3

component = tanjun.Component()
sia = vaderSentiment.SentimentIntensityAnalyzer()


@component.with_slash_command
@tanjun.with_str_slash_option('topic', 'topic to check sentiment on')
@tanjun.with_channel_slash_option('channel', 'channel to limit opinions to', default=None)
@tanjun.as_slash_command('rankedopinion', 'Find out what a channel/server thinks of a topic')
async def rankedopinion(
        ctx: tanjun.abc.Context,
        topic: str,
        channel: typing.Optional[hikari.InteractionChannel],
        db: Database = tanjun.inject(type=Database)
) -> None:
    if not db.check_read_permission(ctx.author):
        await(ctx.respond('In order to use Robot Kirby, please opt in to data collection using the `/opt in` command. '
                          'This will allow me to collect your messages so that I can build sentences from your data. '
                          ':heart:'))
        return

    match channel:
        case None:
            prefix_str = f'**{ctx.get_guild().name}**'
        case hikari.InteractionChannel():
            prefix_str = f'{channel.mention}'
        case _:
            await ctx.respond(f"Something is broken about this query.")
            return

    await ctx.respond(f"Trying to figure out what {prefix_str} thinks about {topic}...")

    # get list of active members, sorted by who has posted the most messages in the past month
    members = [await ctx.rest.fetch_user(x) for x in db.get_active_user_ids()]
    member_msg_count = {}
    one_month_ago = datetime.datetime.today() - relativedelta(month=1)
    for m in members:
        member_msg_count[m] = len(db.get_messages(member=m, since=one_month_ago))
    member_msg_count = collections.OrderedDict(sorted(member_msg_count.items(), key=operator.itemgetter(1)))
    top_members = list(reversed(list(member_msg_count)))

    # get top ten member's opinions on topic
    output = []
    for member in top_members:
        # once we have 10 (or we go through all the members we got) break
        if len(output) >= 10:
            break

        messages = db.get_messages(
            member=member,
            guild=ctx.guild_id,
            channel=channel,
            text=topic
        )
        # skip this member if they don't have messages relating to the topic
        if messages is None or len(messages) == 0:
            continue

        scores = np.array([sia.polarity_scores(m) for m in messages])

        compound = np.asarray([s['compound'] for s in scores])
        neu = np.asarray([s['neu'] for s in scores])

        # weight neutral scores less, opinionated scores more
        try:
            score = np.average(compound, weights=1-neu)
        except ZeroDivisionError:
            score = np.average(compound)

        output.append((score, f'{member.mention} `score={score:.4f}` ({score_to_text(score)[2:]})'))

    if output is None or len(output) == 0:
        await ctx.edit_initial_response(f"{prefix_str} doesn't have an opinion on *{topic}*")
    else:
        output = reversed(sorted(output, key=lambda tup: tup[0]))
        output = [f'{idx}. {e[1]}' for idx, e in enumerate(output)]
        output = '\n'.join(output)
        await ctx.edit_initial_response(f"{prefix_str}'s opinions on *{topic}*:\n"
                                        f"{output}")


@tanjun.as_loader
def load(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
