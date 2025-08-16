### Robot Kirby
Robot Kirby is a Discord bot that can imitate specific users, channels, or servers, based on a Markov chain model.
Users must opt in for their data to be collected using the `/opt in` command.

Robot Kirby uses [Hikari](https://github.com/hikari-py/hikari) and [Tanjun](https://github.com/FasterSpeeding/Tanjun)
for interacting with the Discord API, [MongoDB](https://www.mongodb.com/) as a database, and
[Markovify](https://github.com/jsvine/markovify) for the Markov chain model.

Credit to [Amelia](https://github.com/a-sinclaire) for the idea for the `/timedensity` command! The `/rankedopinion` command was written by [Amelia](https://github.com/a-sinclaire) and the `/similarity` command was written by [Jenna](https://github.com/jemi622).

## How to run

Make a file called `.env` in the root directory with the following contents:

```
DISCORD_TOKEN=<your token from the Discord API developer portal>
```

Then, start the Docker containers:
`docker compose up`

## Discord Permissions & Intents

- Required scopes: `bot`, `applications.commands`.
- Gateway intents (Developer Portal → Bot → Privileged Gateway Intents):
  - Message Content
- Guild permissions (when inviting):
  - View Channels
  - Send Messages
  - Attach Files
  - Embed Links
  - Read Message History

When generating the invite link, include the scopes above and select the listed permissions, or use the Discord Developer Portal’s permission builder.

## CI & Local Checks

This repo uses GitHub Actions to enforce code quality on every PR and push to `master`:

- Formatting: `ruff format` then `ruff check --fix` (fails if changes are needed).
- Type checking: `pyright`.

You can run the same checks locally with `uv`.

### Install uv

`uv` is a fast Python package and environment manager from Astral. Pick one method:

- macOS/Linux (script): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- macOS (Homebrew): `brew install uv`
- Windows (PowerShell): `irm https://astral.sh/uv/install.ps1 | iex`

After installing, restart your shell so `uv` is on your `PATH`.

### Install Task (optional)

`Task` is a simple task runner used by `Taskfile.yml` for common dev commands. Install it if you want to use the provided tasks:

- macOS (Homebrew): `brew install go-task`
- macOS/Linux (script): `sh -c "$(curl -sSL https://taskfile.dev/install.sh)" -- -d`

Verify: `task --version`

### Set up the dev environment

From the repo root:

1) Create a virtual environment: `uv venv`

2) Activate it:
   - macOS/Linux: `source .venv/bin/activate`

3) Install dependencies (including dev tools like Ruff and Pyright):
   - `uv sync --group dev`

### Run checks locally

- Format and autofix: `uv run ruff format && uv run ruff check --fix`
- Type check: `uv run pyright`
- Lint only (no fixes): `uv run ruff check`

If you use Taskfile (optional), the following are equivalent:

- `task format` → runs Ruff format and autofix
- `task typecheck` → runs Pyright for type checking
