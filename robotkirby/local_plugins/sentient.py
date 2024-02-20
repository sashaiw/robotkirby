import random
from random import sample

from robotkirby.db.local_db_driver import Database
import markovify


def sentient(guild, member, channel, topic, prompt, db: Database):
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

    punctuation = ['.', '?', '!']
    sentence = None
    if prompt is None:
        prompt = ''
    if messages is not None and len(messages) > 0:
        model = markovify.Text(messages, retain_original=False)
        if len(prompt) == 0:
            sentence = model.make_sentence(tries=30)
        elif prompt[-1] in punctuation:
            print('ENDED IN PUNCTUATION - GENERATING LIKE NORMAL')
            sentence = prompt + ' ' + model.make_sentence(tries=30)
        else:
            prompt_words = prompt.split(' ')
            valid = False
            if len(prompt_words) >= 2:  # last two in corpus
                init_state = (prompt_words[-2].strip(), prompt_words[-1].strip())
                for m in messages:
                    m_words = m.split(' ')
                    for idx, w in enumerate(m_words):
                        if w == prompt_words[-2]:
                            if idx+1 < len(m_words):
                                if m_words[idx+1] == prompt_words[-1]:
                                    valid = True
                                    break
                if valid:
                    print('LAST TWO MATCHED - STARTING WITH LAST TWO')
                    sentence = ' '.join(prompt_words[:-2]) + ' ' + model.make_sentence(init_state=init_state, tries=30)
            elif len(prompt_words) >= 1 and valid is False:
                # last in corpus ?
                befores = []
                afters = []
                for m in messages:
                    m_words = m.split(' ')
                    for idx, w in enumerate(m_words):
                        if w == prompt_words[-1]:
                            valid = True
                            if idx + 1 < len(m_words):
                                afters.append(m_words[idx+1])
                            if idx - 1 >= 0:
                                befores.append((m_words[idx-1]))
                if valid:
                    print('LAST ONE MATCHED - FINDING PAIRS')
                    after = False
                    if len(befores) > 0 and len(afters) > 0:
                        if random.random() > 0.5:
                            # befores
                            init_state = (sample(befores, 1)[0].strip(), prompt_words[-1].strip())
                        else:
                            # afters
                            after = True
                            init_state = (prompt_words[-1].strip(), sample(afters, 1)[0].strip())
                    elif len(befores) > 0:
                        init_state = (sample(befores, 1)[0].strip(), prompt_words[-1].strip())
                    elif len(afters) > 0:
                        after = True
                        init_state = (prompt_words[-1].strip(), sample(afters, 1)[0].strip())
                    else:
                        init_state = None
                    print(f'len(befores) = {len(befores)}, len(afters) = {len(afters)}')
                    if init_state is not None:
                        print(f'GENERATING STARTING WITH {init_state}')
                        sentence = model.make_sentence(init_state=init_state, tries=30)
                        if not after:
                            sentence = ' '.join(sentence.split(' ')[1:])
                        sentence = ' '.join(prompt_words[:-1]) + ' ' + sentence
                        sentence = sentence[1:]
                    else:
                        sentence = None
            else:
                # otherwise no match
                sentence = None

            # last one in corpus

    if sentence is not None:
        return f"{prefix_str}:\n{sentence}"
    else:
        return f"I don't have enough data for {prefix_str}."
