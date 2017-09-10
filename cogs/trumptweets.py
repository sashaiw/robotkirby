import git
import os
import zipfile
import json
import asyncio

class TrumpTweets:
    def __init__(self,bot):
        self.bot = bot

    async def on_ready(self):
        while True:
            # Update json
            g = git.cmd.Git("db/trump")
            g.pull()

            # Unzip condensed json
            for file in os.listdir("db/trump"):
                if file.startswith("condensed") and file.endswith(".zip"):
                    zipref = zipfile.ZipFile("db/trump/" + file, "r")
                    zipref.extractall(path="db/trump/")
                    zipref.close()

            # Convert json to text file
            markovfile = open("db/markov/trump.txt.swp", "w")
            for file in os.listdir("db/trump"):
                if file.endswith(".json"):
                    with open("db/trump/" + file) as jsonfile:
                        j = json.load(jsonfile)
                        for tweet in j:
                            markovfile.write(tweet["text"] + "\n")
            markovfile.close()
            os.rename("db/markov/trump.txt.swp", "db/markov/trump.txt")
            print("Updated tweets!")
            
            await asyncio.sleep(3600)

def setup(bot):
    bot.add_cog(TrumpTweets(bot))
