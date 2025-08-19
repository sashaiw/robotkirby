import io
import re

# The wordcloud library spams DeprecationWarnings, might want to find a solution eventually
import warnings
from typing import Optional

import hikari
import tanjun
from wordcloud import WordCloud

from robotkirby.db.db_driver import Database

warnings.filterwarnings("ignore", category=DeprecationWarning)

component = tanjun.Component()


@component.with_slash_command
@tanjun.with_member_slash_option(
    "member", "member to generate wordcloud for", default=None
)
@tanjun.with_channel_slash_option(
    "channel", "channel to generate wordcloud for", default=None
)
@tanjun.as_slash_command("wordcloud", "Create wordcloud for server/member/channel")
async def wordcloud(
    ctx: tanjun.abc.Context,
    member: Optional[hikari.Member],
    channel: Optional[hikari.InteractionChannel],
    db: Database = tanjun.inject(type=Database),
) -> None:
    if not db.check_read_permission(ctx.author):
        await ctx.respond(
            "In order to use Robot Kirby, please opt in to data collection using the `/opt in` command. "
            "This will allow me to collect your messages so that I can build sentences from your data. "
            ":heart:"
        )
        return

    guild = ctx.get_guild()
    guild_name = guild.name if guild is not None else "this server"
    match (member, channel):
        case (None, None):
            prefix_str = f"**{guild_name}**"
        case (hikari.Member(), None):
            prefix_str = f"{member.mention}"
        case (None, hikari.InteractionChannel()):
            prefix_str = f"{channel.mention}"
        case (hikari.Member(), hikari.InteractionChannel()):
            prefix_str = f"{member.mention} in {channel.mention}"
        case _:
            await ctx.respond("Something is broken about this query.")
            return

    await ctx.respond(f"Thinking about {prefix_str}...")

    messages = db.get_messages(member=member, guild=ctx.guild_id, channel=channel)

    if messages is not None and len(messages) > 0:
        text = " ".join(messages)
        text = re.sub(r"http\S+", "", text)

        img = io.BytesIO()

        try:
            (
                WordCloud(
                    width=1280,
                    height=720,
                    background_color="#36393e",
                    colormap="spring",
                )
                .generate(text)
                .to_image()
                .save(img, format="PNG")
            )
        except ValueError:
            await ctx.edit_initial_response(
                f"I don't have enough data for {prefix_str}."
            )
            return

        await ctx.edit_initial_response(
            prefix_str, attachment=hikari.Bytes(img.getvalue(), "cloud.png")
        )
    else:
        await ctx.edit_initial_response(f"I don't have enough data for {prefix_str}.")


@tanjun.as_loader
def load(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
