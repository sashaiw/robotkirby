import hikari
import tanjun
import typing
from robotkirby.db.db_driver import Database
from wordcloud import WordCloud
import re
import io

# The wordcloud library spams DeprecationWarnings, might want to find a solution eventually
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

component = tanjun.Component()


@component.with_slash_command
@tanjun.with_member_slash_option('member', 'member to generate wordcloud for', default=None)
@tanjun.with_channel_slash_option('channel', 'channel to generate wordcloud for', default=None)
@tanjun.as_slash_command('wordcloud', 'Create wordcloud for server/member/channel')
async def wordcloud(
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

    if messages is not None:
        text = ' '.join(messages)
        text = re.sub(r'http\S+', '', text)

        img = io.BytesIO()

        cloud = WordCloud(
            width=1280,
            height=720,
            background_color='#36393e',
            colormap='spring'
        ).generate(text).to_image().save(img, format='PNG')

        await ctx.respond(prefix_str, attachment=hikari.Bytes(img.getvalue(), 'cloud.png'))
    else:
        await ctx.respond(f"I don't have enough data for {prefix_str}.")


@tanjun.as_loader
def load(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
