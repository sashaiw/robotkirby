import hikari
from robotkirby.db.local_db_driver import Database
import markovify


def sentient(guild, member, channel, db: Database):
    match (member, channel):
        case (None, None):
            prefix_str = f'**{guild["name"]}**'  # server name / dm title (maybe could use folder title or something)
        case (member, None):
            prefix_str = f'{member["name"]}'  # member name
        case (None, channel):
            prefix_str = f'{channel["name"]}'  # channel name
        case (member, channel):
            prefix_str = f'{member["name"]} in {channel["name"]}'  # member in channel
        case _:
            raise Exception(f"Something is broken about this query.")

    print(f"Thinking about {prefix_str}...")

    messages = db.get_messages(
        member=member,
        guild=guild,
        channel=channel,
        text=None
    )

    sentence = None
    if messages is not None and len(messages) > 0:
        model = markovify.Text(messages)
        sentence = model.make_sentence()

    if sentence is not None:
        return f"{prefix_str}:\n{sentence}"
    else:
        return f"I don't have enough data for {prefix_str}."
