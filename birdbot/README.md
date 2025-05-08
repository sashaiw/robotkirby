# birdbot
A Discord bot that posts daily updates from a [BirdNET-Go](https://github.com/tphakala/birdnet-go) server using a mySQL
backend.

# Configuration
Make sure that your BirdNET-Go instance is configured to use a MySQL backend. This bot will work for multiple nodes
that log to the same database.

# Running (Docker)
Create a `.env` with the following contents:
```
DISCORD_TOKEN=<token from Discord developer portal>
UPDATE_CHANNEL_ID=<channel ID to post daily updates in>

MYSQL_HOST=birdnet
MYSQL_DATABASE=birdnet
MYSQL_USER=birdnet
MYSQL_PASSWORD=secret
```

Create a `compose.yaml` file with the following contents:
```
services:
  birdbot:
    build: .
    container_name: birdbot
    env_file: .env
    restart: unless-stopped
```

Then, run `docker compose up`.

# Future work
- Make post time configurable (right now it always happens daily at 10:00 PM)
- Make confidence/observation thresholds configurable
- Figure out what happens when mixing nodes with multiple timezones
- Comment and clean up code