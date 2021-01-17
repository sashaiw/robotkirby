import re
from discord.ext import commands
import markovify
import discord
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


class Sentient(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users = {}

    @commands.command(pass_context=True, description="Uses Markov chains to emulate users. Pass mention as arg.")
    async def sentient(self, ctx, arg : str):
        role = discord.utils.get(ctx.message.author.guild.roles, name='Robot Kirby subject')
        if ctx.message.author.roles is not None and role in ctx.message.author.roles:
            prefix = ''
            try:
                mentionid = ctx.message.mentions[0].id
                if ctx.message.mentions[0].nick is not None:
                    prefix = f'**{ctx.message.mentions[0].nick}: **'
                else:
                    prefix = f'**{ctx.message.mentions[0].name}: **'
            except IndexError:
                mentionid = arg

            try:
                with open(f"db/markov/{mentionid}.txt") as f:
                    text = f.read()
            except FileNotFoundError:
                text = ""

            with open("db/markov/creepy.txt") as f:
                creepy_text = f.read()

            if ctx.message.author.id not in self.users:
                self.users[ctx.message.author.id] = User(mentionid)

            self.users[ctx.message.author.id].inc_creep(0.05, mentionid)

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
                await ctx.send("`INSUFFICIENT DATA`")
            else:
                sentence = re.sub("<@!?[0-9]{16,32}>|@everyone|https?:\/\/discord.* ?", "", sentence)

                await ctx.send(prefix + sentence)
        else:
            await ctx.send('You have not opted in to data collection and are not authorized to use this command. '
                           'Use `!optin` to opt in.')

def setup(bot):
    bot.add_cog(Sentient(bot))
