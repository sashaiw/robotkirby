import collections
import datetime
import operator

import hikari
import tanjun
from dateutil.relativedelta import relativedelta
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from robotkirby.db.db_driver import Database

component = tanjun.Component()


def score_to_text(score: float) -> str:
    ranges = {
        "a **slightly similar**": (0, 0.2),
        "a **somewhat similar**": (0.2, 0.4),
        "a **moderately similar**": (0.4, 0.6),
        "a **strongly similar**": (0.6, 0.8),
        "an **extremely similar**": (0.8, 1.0),
    }

    for name, r in ranges.items():
        if r[0] <= score <= r[1]:
            return name
    return "a **slightly similar**"


@component.with_slash_command
@tanjun.with_member_slash_option("member", "user to check similarity on")
@tanjun.as_slash_command("similarity", "Find out who is most similar to a member")
async def similarity(
    ctx: tanjun.abc.Context,
    member: hikari.Member,
    db: Database = tanjun.inject(type=Database),
) -> None:
    if not db.check_read_permission(ctx.author):
        await ctx.respond(
            "In order to use Robot Kirby, please opt in to data collection using the `/opt in` command. "
            "This will allow me to collect your messages so that I can build sentences from your data. "
            ":heart:"
        )
        return

    await ctx.respond(
        f"Trying to figure out who is most similar to {f'{member.mention}'}..."
    )

    # get list of active members, sorted by who has posted the most messages in the past month (other than the member to be compared)
    members_ids = db.get_unique_user_ids(guild=ctx.guild_id)
    try:
        members_ids.remove(member.id)
    except ValueError:
        pass
    member_msg_count = {}
    one_month_ago = datetime.datetime.today() - relativedelta(month=1)
    for idx, m_id in enumerate(members_ids):
        member_msg_count[m_id] = db.messages.count_documents(
            {"author": m_id, "time": {"$gte": one_month_ago}}
        )
        await ctx.edit_initial_response(f"Preprocessing: {idx / len(members_ids):.2%}")
    member_msg_count = collections.OrderedDict(
        sorted(member_msg_count.items(), key=operator.itemgetter(1))
    )
    top_members = list(reversed(list(member_msg_count)))

    comparison_member_messages = "".join(
        db.get_messages(member=member.id, guild=ctx.guild_id)
    )

    # get top ten member's similarity to the member to be compared
    output: list[tuple[float, str]] = []
    for member_id in top_members:
        # once we have 10 (or we go through all the members we got) break
        if len(output) >= 10:
            break

        messages = db.get_messages(member=member_id, guild=ctx.guild_id)
        # skip this member if they don't have messages
        if messages is None or len(messages) == 0:
            continue

        current_member_messages = "".join(messages)

        vectorizer = CountVectorizer()
        vectors = vectorizer.fit_transform(
            [comparison_member_messages, current_member_messages]
        )
        similarity_score = cosine_similarity(vectors[0], vectors[1])[0][0]

        current_member = await ctx.rest.fetch_user(member_id)
        output.append(
            (
                similarity_score,
                f"{current_member.mention} `score={similarity_score:.4f}` ({score_to_text(similarity_score)[2:]})",
            )
        )
        final_output = reversed(sorted(output, key=lambda tup: tup[0]))
        final_output = [f"{idx}. {e[1]}" for idx, e in enumerate(final_output)]
        final_output = "\n".join(final_output)
        await ctx.edit_initial_response(
            f"Here's who is most similar to {f'{member.mention}'}:\n{final_output}"
        )

    if output is None or len(output) == 0:
        await ctx.edit_initial_response(f"No one is similar to {f'{member.mention}'}")
    else:
        final_output = reversed(sorted(output, key=lambda tup: tup[0]))
        final_output = [f"{idx}. {e[1]}" for idx, e in enumerate(final_output)]
        final_output = "\n".join(final_output)
        await ctx.edit_initial_response(
            f"Here's who is most similar to {f'{member.mention}'}:\n{final_output}"
        )


@tanjun.as_loader
def load(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
