### Robot Kirby
Robot Kirby is a Discord bot that can imitate specific users, channels, or servers, based on a Markov chain model.
Users must opt in for their data to be collected using the `/opt in` command.

Robot Kirby uses [Hikari](https://github.com/hikari-py/hikari) and [Tanjun](https://github.com/FasterSpeeding/Tanjun)
for interacting with the Discord API, [MongoDB](https://www.mongodb.com/) as a database, and 
[Markovify](https://github.com/jsvine/markovify) for the Markov chain model.

## How to run

Make a file called `.env` in the root directory with the following contents:

```
DISCORD_TOKEN=<your token from the Discord API developer portal>
```

Then, start the Docker containers:
`docker compose up`
