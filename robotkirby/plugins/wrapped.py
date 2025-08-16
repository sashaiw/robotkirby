import hikari
import tanjun
import typing
import datetime
import time
import re
import io
import collections
from robotkirby.db.db_driver import Database

from wordcloud import WordCloud
import numpy as np
import profanity_check
from vaderSentiment import vaderSentiment
sia = vaderSentiment.SentimentIntensityAnalyzer()

import nltk
nltk.download('punkt')
nltk.download('stopwords')

component = tanjun.Component()


@component.with_slash_command
@tanjun.as_slash_command('wrapped', 'Initiate Robot Kirby Wrapped (only for Sasha)')
async def wrapped(
        ctx: tanjun.abc.Context,
        db: Database = tanjun.inject(type=Database)
) -> None:
    if ctx.author.id != 89398547308380160:
        await ctx.respond('no', delete_after=1)
        return

    # members = [await ctx.rest.fetch_user(x) for x in [89398547308380160, 89398547308380160, 89398547308380160]]
    members = [await ctx.rest.fetch_user(x) for x in db.get_all_opted_in_user_ids()]
    await ctx.respond(f"Deploying Robot Kirby Wrapped to {len(members)} users.")

    for member in members:
        messages = db.get_messages(
            since=datetime.datetime(datetime.datetime.now().year, 1, 1, 0, 0, 0, 0),
            member=member
        )

        channels = db.get_channels(
            since=datetime.datetime(datetime.datetime.now().year, 1, 1, 0, 0, 0, 0),
            member=member
        )

        if len(messages) > 100:
            try:
                # generate wordcloud
                text = ' '.join(messages)
                text = re.sub(r'http\S+', '', text)
                img = io.BytesIO()
                cloud = WordCloud(
                    width=1280,
                    height=720,
                    background_color='#36393e',
                    colormap='spring'
                ).generate(text).to_image().save(img, format='PNG')

                # tokenize
                tokens = []
                stopwords = nltk.corpus.stopwords.words('english')
                for message in messages:
                    tokens += [token for token in nltk.WhitespaceTokenizer().tokenize(message.lower())
                               if token not in stopwords]

                # frequency distribution
                fdist = nltk.FreqDist(nltk.ngrams(tokens, 1))
                most_common = fdist.most_common(5)

                # channel frequency distribution
                channel_freq = collections.Counter(channels)
                most_common_channels = channel_freq.most_common(5)

                # detect profanity
                profanity = profanity_check.predict(messages)
                profanity_score = np.count_nonzero(profanity) / profanity.size

                # positivity
                sentiment = np.array([sia.polarity_scores(m) for m in messages])
                sentiment_compound = np.asarray([s['compound'] for s in sentiment])
                # sentiment_neu = np.asarray([s['neu'] for s in sentiment])
                # sentiment_pos = np.asarray([s['pos'] for s in sentiment])
                # sentiment_neg = np.asarray([s['neg'] for s in sentiment])

                n_pos = np.count_nonzero(sentiment_compound > 0.05)
                n_neu = np.count_nonzero((-0.05 < sentiment_compound) & (sentiment_compound < 0.05))
                n_neg = np.count_nonzero(sentiment_compound < -0.05)

                await member.send(
                    f"# Robot Kirby: Wrapped\n"
                    f"Congratulations! You are one of Robot Kirby's top users, having logged a total of **{len(messages)}** "
                    f"messages this year. Here is a wordcloud of what you said this year:",
                    attachment=hikari.Bytes(img.getvalue(), 'cloud.png')
                )

                await(member.send(
                    f"## Top Words\n"
                    f"Here are some of your most used words this year:\n"
                    f"**1.** `{most_common[0][0][0]}` ({most_common[0][1]})\n"
                    f"**2.** `{most_common[1][0][0]}` ({most_common[1][1]})\n"
                    f"**3.** `{most_common[2][0][0]}` ({most_common[2][1]})\n"
                    f"**4.** `{most_common[3][0][0]}` ({most_common[3][1]})\n"
                    f"**5.** `{most_common[4][0][0]}` ({most_common[4][1]})\n"
                ))

                await(member.send(
                    f"## Top Channels\n"
                    f"Here are the channels you posted in the most this year:\n"
                    f"**1.** <#{most_common_channels[0][0]}> ({most_common_channels[0][1]} messages)\n"
                    f"**2.** <#{most_common_channels[1][0]}> ({most_common_channels[1][1]} messages)\n"
                    f"**3.** <#{most_common_channels[2][0]}> ({most_common_channels[2][1]} messages)\n"
                    f"**4.** <#{most_common_channels[3][0]}> ({most_common_channels[3][1]} messages)\n"
                    f"**5.** <#{most_common_channels[4][0]}> ({most_common_channels[4][1]} messages)\n"
                ))

                if n_pos > n_neu and n_pos > n_neg:
                    await(member.send(
                        f"## Positivity\n"
                        f"Your messages were mostly positive this year!\n"
                        f"- **{(n_pos / len(messages)) * 100:.2f}%** positive\n"
                        f"- **{(n_neu / len(messages)) * 100:.2f}%** neutral\n"
                        f"- **{(n_neg / len(messages)) * 100:.2f}%** negative\n"
                        f"Let's hope {datetime.datetime.now().year} brings more good vibes!"
                    ))
                if n_neu > n_pos and n_neu > n_neg:
                    await(member.send(
                        f"## Positivity\n"
                        f"Your messages were mostly neutral this year.\n"
                        f"- **{(n_pos / len(messages)) * 100:.2f}%** positive\n"
                        f"- **{(n_neu / len(messages)) * 100:.2f}%** neutral\n"
                        f"- **{(n_neg / len(messages)) * 100:.2f}%** negative\n"
                    ))
                if n_neg > n_pos and n_neg > n_neu:
                    await(member.send(
                        f"## Positivity\n"
                        f"Your messages were mostly negative this year.\n"
                        f"- **{(n_pos.size / len(messages)) * 100:.2f}%** positive\n"
                        f"- **{(n_neu.size / len(messages)) * 100:.2f}%** neutral\n"
                        f"- **{(n_neg.size / len(messages)) * 100:.2f}%** negative\n"
                        f"You doing alright?"
                    ))

                await(member.send(
                    f"## Offensive Language\n"
                    f"**{profanity_score * 100:.2f}%** of your messages this year contained offensive language."
                ))
            except:
                print(f"{member.id} failed!")

            time.sleep(5)

    await ctx.edit_initial_response('Done!')

@tanjun.as_loader
def load(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
