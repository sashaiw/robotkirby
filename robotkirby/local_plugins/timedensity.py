from robotkirby.db.local_db_driver import Database
import io
from datetime import datetime
from zoneinfo import ZoneInfo
from dateutil import tz
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

sns.set_theme()
sns.set(
    rc={
        'axes.facecolor': '#36393e',
        'figure.facecolor': '#36393e',
        'axes.labelcolor': 'white',
        'grid.color': '#99aab5',
        'text.color': 'white',
        'xtick.color': '#99aab5',
        'ytick.color': '#99aab5'
    }
)

utc_tz = tz.tzutc()


# local_tz = tz.tzlocal()


def make_prefix_str(guild, member, channel, topic, db):
    guild_name = 'ALL GUILDS' if guild is None else guild["name"]
    channel_name = '???'
    if channel is not None:
        channel_name = db.get_dm_name(guild=guild, channel=channel) if guild_name == 'Direct Messages' else \
            channel['name']
    match (member, channel, topic):
        case (None, None, None):
            return f'in **{guild_name}**'
        case (member, None, None):
            return f'by {member["name"]}'
        case (None, channel, None):
            return f'in {channel_name}'
        case (member, channel, None):
            return f'{member["name"]} in {channel_name}'
        case (None, None, str):
            return f'in **{guild_name}** about *{topic}*'
        case (member, None, str):
            return f'by {member["name"]} about *{topic}*'
        case (None, channel, str):
            return f'in {channel_name} about *{topic}*'
        case (member, channel, str):
            return f'in {member["name"]} in {channel_name} about *{topic}*'
        case _:
            return None


def utc_to_local(dt: datetime, tz_code: str) -> datetime:
    local_tz = tz.gettz(tz_code)

    utctime = dt.replace(tzinfo=utc_tz)
    return utctime.astimezone(local_tz)


def dt_to_sec(dt: datetime) -> int:
    """convert datetime object to seconds from beginning of day"""
    time = dt.time()
    return (time.hour * 60 + time.minute) * 60 + time.second


def timedensity(guild, topic, member, channel, timezone, db) -> None:
    prefix_str = make_prefix_str(guild, member, channel, topic, db)

    print(f"Thinking about posts {prefix_str}...")

    if tz.gettz(timezone) is None:
        print(f'***{timezone}*** is not a valid timezone!')
        return

    timestamps = db.get_timestamps(
        member=member,
        guild=guild,
        channel=channel,
        text=topic
    )

    if timestamps is not None and len(timestamps) > 0:
        df = pd.DataFrame([dt_to_sec(utc_to_local(t, timezone)) for t in timestamps], columns=['time'])

        img = io.BytesIO()

        graph = sns.displot(
            data=df,
            x='time',
            kind='kde',
            rug=True,
            color="#ffa6c9",
            height=4,
            aspect=2,
        )

        graph.ax.set(xlabel=f'Time ({timezone})')
        graph.ax.set(title=f'')
        graph.ax.set_xlim(0, 86400)
        graph.ax.xaxis.set_major_locator(ticker.MultipleLocator(7200))
        graph.ax.xaxis.set_major_formatter(
            ticker.FuncFormatter(
                lambda x, pos: f'{x // 3600:02.0f}:{x % 3600 // 60:02.0f}'
            )
        )

        graph.figure.show()
        # graph.figure.savefig(img, format='png')
        # await ctx.edit_initial_response(f'Posts {prefix_str}',
        #                                 attachment=hikari.Bytes(img.getvalue(), 'timedensity.png'))

    else:
        print(f"I don't have enough data for {prefix_str}")
