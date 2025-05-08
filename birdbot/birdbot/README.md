# Sample .env
```
DISCORD_TOKEN=<token from the Discord API developer portal>
UPDATE_CHANNEL_ID=<channel ID to post updates to>
```

# Sample `compose.yml`
```yaml
services:
  birdbot:
    build: .
    container_name: birdbot
    env_file: .env
    environment:
      DB_URI: "localhost"
    restart: always
```