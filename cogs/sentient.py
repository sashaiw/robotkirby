import re
from discord.ext import commands
import markovify
from cogs.utils import checks


class User:
    def __init__(self, last_user):
        self.creep_factor = 0
        self.last_user = ""

    def inc_creep(self, amt, current_user):
        if current_user == self.last_user:
            self.creep_factor += amt
        else:
            self.creep_factor = 0

        self.last_user = current_user


class Sentient:
    def __init__(self, bot):
        self.bot = bot
        self.users = {}

    @commands.command(pass_context=True, description="Uses Markov chains to emulate users. Pass mention as arg.")
    @checks.is_licensed()
    async def sentient(self, ctx, arg : str):
        try:
            mentionid = ctx.message.mentions[0].id
        except IndexError:
            mentionid = arg
        try:
            with open("db/markov/" + mentionid + ".txt") as f:
                text = f.read()
        except FileNotFoundError:
            text = ""

        with open("db/markov/creepy.txt") as f:
            creepy_text = f.read()

        if ctx.message.author.id not in self.users:
            self.users[ctx.message.author.id] = User(mentionid)

        self.users[ctx.message.author.id].inc_creep(0.2, mentionid)

        #await self.bot.say("`Current creep factor: " + str(self.users[ctx.message.author.id].creep_factor) + "`")

        if self.users[ctx.message.author.id].creep_factor > 2:
            creep_weight = self.users[ctx.message.author.id].creep_factor
        else:
            creep_weight = 0

        model = markovify.NewlineText(text)
        creepy_model = markovify.NewlineText(creepy_text)

        model_combo = markovify.combine([model, creepy_model], [1, creep_weight])

        sentence = model_combo.make_sentence(tries=100)
        if sentence is None:
            await self.bot.say("`INSUFFICIENT DATA`")
        else:
            sentence = re.sub("<@!?[0-9]{16,32}>|@everyone|https?:\/\/discord.* ?", "", sentence)
            await self.bot.say(sentence)

def setup(bot):
    bot.add_cog(Sentient(bot))
