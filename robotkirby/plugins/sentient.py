import re
import typing

import hikari
import markovify
import tanjun

from robotkirby.db.db_driver import Database

word_split_pattern = re.compile(r"\s+")


def word_split(sentence):
    """
    Splits a sentence into a list of words.
    """
    return re.split(word_split_pattern, sentence)


component = tanjun.Component()


@component.with_slash_command
@tanjun.with_member_slash_option('member', 'user to imitate', default=None)
@tanjun.with_channel_slash_option('channel', 'channel to imitate', default=None)
@tanjun.with_str_slash_option('topic', 'topic to imitate', default=None)
@tanjun.with_str_slash_option('prompt', 'start of sentence', default=None)
@tanjun.as_slash_command('sentient', 'Imitate user')
async def sentient(
        ctx: tanjun.abc.Context,
        member: typing.Optional[hikari.Member],
        channel: typing.Optional[hikari.InteractionChannel],
        topic: str,
        prompt: str,
        db: Database = tanjun.inject(type=Database)
) -> None:
    if not db.check_read_permission(ctx.author):
        await(ctx.respond('In order to use Robot Kirby, please opt in to data collection using the `/opt in` command. '
                          'This will allow me to collect your messages so that I can build sentences from your data. '
                          ':heart:'))
        return

    match (member, channel, topic):
        case (None, None, None):
            prefix_str = f'**{ctx.get_guild().name}**'
        case (hikari.Member(), None, None):
            prefix_str = f'{member.mention}'
        case (None, hikari.InteractionChannel(), None):
            prefix_str = f'{channel.mention}'
        case (hikari.Member(), hikari.InteractionChannel(), None):
            prefix_str = f'{member.mention} in {channel.mention}'
        case (None, None, str_):
            prefix_str = f'**{ctx.get_guild().name}** about *{topic}*'
        case (hikari.Member(), None, str_):
            prefix_str = f'{member.mention} about *{topic}*'
        case (None, hikari.InteractionChannel(), str_):
            prefix_str = f'{channel.mention} about *{topic}*'
        case (hikari.Member(), hikari.InteractionChannel(), str_):
            prefix_str = f'{member.mention} in {channel.mention} about *{topic}*'
        case _:
            await ctx.respond(f"Something is broken about this query.")
            return None

    if prompt is not None:
        prefix_str += f' with prompt *"{prompt}"*'

    await ctx.respond(f"Thinking about {prefix_str}...")

    messages = db.get_messages(
        member=member,
        guild=ctx.guild_id,
        channel=channel,
        text=topic
    )

    state_size = 2
    n_tries = 30
    sentence = None

    if messages is not None and len(messages) > 0:
        model = markovify.Text(messages, state_size=state_size)  # build markov model

        # if no prompt given generate like normal
        if prompt is None or len(prompt) == 0:
            sentence = model.make_sentence(tries=n_tries)
        else:
            prefix = []
            prompt_split = word_split(prompt)
            while len(prompt_split) > state_size:
                prefix.append(prompt_split.pop(0))
            prompt = ' '.join(prompt_split)

            try:
                markov = model.make_sentence_with_start(beginning=prompt, tries=n_tries)
            except Exception:
                markov = None

            if markov is not None:
                prefix = f'{" ".join(prefix)} ' if len(prefix) != 0 else ''
                sentence = f'{prefix}{markov}'

    if sentence is not None:
        await ctx.edit_initial_response(f"{prefix_str}:\n{sentence}")
    else:
        await ctx.edit_initial_response(f"I don't have enough data for {prefix_str}.")


@tanjun.as_loader
def load(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
