import typing
from robotkirby.db.local_db_driver import Database
from wordcloud import WordCloud
import re
import io

# The wordcloud library spams DeprecationWarnings, might want to find a solution eventually
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)


def wordcloud(guild, member, channel, db) -> str:
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
            return f"Something is broken about this query."

    print(f"Thinking about {prefix_str}...")

    messages = db.get_messages(
        member=member,
        guild=guild,
        channel=channel,
        text=None
    )

    if len(messages) > 0 or messages is not None:
        text = ' '.join(messages)
        text = re.sub(r'http\S+', '', text)

        img = io.BytesIO()

        try:
            cloud = WordCloud(
                width=1280,
                height=720,
                background_color='#36393e',
                colormap='spring'
            ).generate(text).to_image().show()#save(img, format='PNG')
        except ValueError:
            return f"I don't have enough data for {prefix_str}."

        return str(prefix_str)
    else:
        return f"I don't have enough data for {prefix_str}."
