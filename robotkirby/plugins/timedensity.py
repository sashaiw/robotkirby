import io
import typing
from datetime import datetime

import hikari
import matplotlib.ticker as ticker
import pandas as pd
import seaborn as sns
import tanjun
from dateutil import tz

from robotkirby.db.db_driver import Database

sns.set_theme()
sns.set(
    rc={
        "axes.facecolor": "#36393e",
        "figure.facecolor": "#36393e",
        "axes.labelcolor": "white",
        "grid.color": "#99aab5",
        "text.color": "white",
        "xtick.color": "#99aab5",
        "ytick.color": "#99aab5",
    }
)

component = tanjun.Component()

utc_tz = tz.tzutc()
# local_tz = tz.tzlocal()


def make_prefix_str(ctx, member, channel, topic):
    match (member, channel, topic):
        case (None, None, None):
            return f"in **{ctx.get_guild().name}**"
        case (hikari.Member(), None, None):
            return f"by {member.mention}"
        case (None, hikari.InteractionChannel(), None):
            return f"in {channel.mention}"
        case (hikari.Member(), hikari.InteractionChannel(), None):
            return f"{member.mention} in {channel.mention}"
        case (None, None, str()):
            return f"in **{ctx.get_guild().name}** about *{topic}*"
        case (hikari.Member(), None, str()):
            return f"by {member.mention} about *{topic}*"
        case (None, hikari.InteractionChannel(), str()):
            return f"in {channel.mention} about *{topic}*"
        case (hikari.Member(), hikari.InteractionChannel(), str()):
            return f"in {member.mention} in {channel.mention} about *{topic}*"
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


@component.with_slash_command
@tanjun.with_str_slash_option("topic", "topic to plot", default=None)
@tanjun.with_member_slash_option("member", "user to plot", default=None)
@tanjun.with_channel_slash_option("channel", "channel to plot", default=None)
@tanjun.with_str_slash_option("timezone", "timezone to report in", default="EST")
@tanjun.as_slash_command(
    "timedensity", "Plot when a member/channel/server is active during the day"
)
async def timedensity(
    ctx: tanjun.abc.Context,
    topic: typing.Optional[str],
    member: typing.Optional[hikari.Member],
    channel: typing.Optional[hikari.InteractionChannel],
    timezone: typing.Optional[str],
    db: Database = tanjun.inject(type=Database),
) -> None:
    if not db.check_read_permission(ctx.author):
        await ctx.respond(
            "In order to use Robot Kirby, please opt in to data collection using the `/opt in` command. "
            "This will allow me to collect your messages so that I can build sentences from your data. "
            ":heart:"
        )
        return

    prefix_str = make_prefix_str(ctx, member, channel, topic)

    await ctx.respond(f"Thinking about posts {prefix_str}...")

    if tz.gettz(timezone) is None:
        await ctx.edit_initial_response(f"***{timezone}*** is not a valid timezone!")
        return

    timestamps = db.get_timestamps(
        member=member, guild=ctx.guild_id, channel=channel, text=topic
    )

    if timestamps is not None and len(timestamps) > 0:
        df = pd.DataFrame(
            [dt_to_sec(utc_to_local(t, timezone)) for t in timestamps], columns=["time"]
        )

        img = io.BytesIO()

        graph = sns.displot(
            data=df,
            x="time",
            kind="kde",
            rug=True,
            color="#ffa6c9",
            height=4,
            aspect=2,
        )

        graph.ax.set(xlabel=f"Time ({timezone})")
        graph.ax.set(title="")
        graph.ax.set_xlim(0, 86400)
        graph.ax.xaxis.set_major_locator(ticker.MultipleLocator(7200))
        graph.ax.xaxis.set_major_formatter(
            ticker.FuncFormatter(
                lambda x, pos: f"{x // 3600:02.0f}:{x % 3600 // 60:02.0f}"
            )
        )

        graph.figure.savefig(img, format="png")
        await ctx.edit_initial_response(
            f"Posts {prefix_str}",
            attachment=hikari.Bytes(img.getvalue(), "timedensity.png"),
        )

    else:
        await ctx.edit_initial_response(f"I don't have enough data for {prefix_str}")


@tanjun.as_loader
def load(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
