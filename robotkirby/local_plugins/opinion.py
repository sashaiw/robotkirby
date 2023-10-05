import typing
from robotkirby.db.local_db_driver import Database
import numpy as np
from statistics import mean
from vaderSentiment import vaderSentiment

vaderSentiment.SPECIAL_CASES['based'] = 3

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


def opinion(guild, topic, member, channel, db):
    if topic is None:
        return "TOPIC REQUIRED"
    guild_name = 'ALL GUILDS' if guild is None else guild["name"]
    channel_name = '???'
    if channel is not None:
        channel_name = db.get_dm_name(guild=guild, channel=channel) if guild_name == 'Direct Messages' else \
            channel['name']
    match (member, channel):
        case (None, None):
            prefix_str = f'**{guild_name}**'
        case (member, None):
            prefix_str = f'{member["name"]}'
        case (None, channel):
            prefix_str = f'{channel_name}'
        case (member, channel):
            prefix_str = f'{member["name"]} in {channel_name}'
        case _:
            print(f"Something is broken about this query.")
            return

    print(f"Trying to figure out what {prefix_str} thinks about {topic}...")

    messages = db.get_messages(
        member=member,
        guild=guild,
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

        return(f"{prefix_str} has {score_to_text(score)} opinion of *{topic}*.\n"
                                        f"`score={score:.4f}`")
    else:
        return(f"{prefix_str} doesn't have an opinion on *{topic}*")
