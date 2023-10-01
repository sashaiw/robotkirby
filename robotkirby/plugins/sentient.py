import hikari
from robotkirby.db.db_driver import Database
import markovify


def sentient(ctx, member, channel, db: Database):
    match (member, channel):
        case (None, None):
            prefix_str = f'**{ctx.get_guild().name}**'  # server name / dm title (maybe could use folder title or something)
        case (member, None):
            prefix_str = f'{member}'  # member name
        case (None, channel):
            prefix_str = f'{channel}'  # channel name
        case (member, channel):
            prefix_str = f'{member} in {channel}'  # member in channel
        case _:
            raise Exception(f"Something is broken about this query.")

    print(f"Thinking about {prefix_str}...")

    messages = db.get_messages(
        member=member,
        guild=ctx.guild_id,
        channel=channel
    )

    sentence = None
    if messages is not None and len(messages) > 0:
        model = markovify.Text(messages)
        sentence = model.make_sentence()

    if sentence is not None:
        return f"{prefix_str}:\n{sentence}"
    else:
        return f"I don't have enough data for {prefix_str}."
