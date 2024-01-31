from robotkirby.db.local_db_driver import Database
import markovify


def sentient(guild, member, channel, topic, db: Database):
    guild_name = f'**ALL GUILDS**' if guild == None else f'**{guild["name"]}**'
    channel_name = '???'
    if channel is not None:
        channel_name = db.get_dm_name(guild=guild, channel=channel) if guild_name == 'Direct Messages' else \
            channel['name']
    match (member, channel, topic):
        case (None, None, None):
            prefix_str = f'{guild_name}'
        case (member, None, None):
            prefix_str = f'{member["name"]}'
        case (None, channel, None):
            if guild_name == f'**Direct Messages**':
                prefix_str = f'{db.get_dm_name(guild=guild, channel=channel)}'
            else:
                prefix_str = f'{channel["name"]}'  # channel name
        case (member, channel, None):
            if guild_name == f'**Direct Messages**':
                prefix_str = f'{member["name"]} in {db.get_dm_name(guild=guild, channel=channel)}'
            else:
                prefix_str = f'{member["name"]} in {channel["name"]}'  # member in channel
        case (None, None, str):
            prefix_str = f'{guild_name} regarding *{topic}*'
        case (member, None, str):
            prefix_str = f'{member["name"]} regarding *{topic}*'
        case (None, channel, str):
            if guild_name == f'**Direct Messages**':
                prefix_str = f'{db.get_dm_name(guild=guild, channel=channel)} regarding *{topic}*'
            else:
                prefix_str = f'{channel["name"]} regarding *{topic}*'  # channel name
        case (member, channel, str):
            if guild_name == f'**Direct Messages**':
                prefix_str = f'{member["name"]} in {db.get_dm_name(guild=guild, channel=channel)} regarding *{topic}*'
            else:
                prefix_str = f'{member["name"]} in {channel["name"]} regarding *{topic}*'  # member in channel
        case _:
            raise Exception(f"Something is broken about this query.")

    print(f"Thinking about {prefix_str}...")

    messages = db.get_messages(
        member=member,
        guild=guild,
        channel=channel,
        text=topic
    )

    sentence = None
    if messages is not None and len(messages) > 0:
        model = markovify.Text(messages, retain_original=False)
        sentence = model.make_sentence(tries=30)

    if sentence is not None:
        return f"{prefix_str}:\n{sentence}"
    else:
        return f"I don't have enough data for {prefix_str}."
