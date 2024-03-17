# PuzzleHunt bot!

A simple discord bot that handles team and puzzle logistic for an online puzzle hunt!

This bot was used to run the inter-uni UNSW - USYD - UTS Battle for Puzzleverse hunt: https://discord.gg/wqyuN93raj.

## Running the bot locally

Note: It's recommended that you set up a [python venv](https://docs.python.org/3/library/venv.html).

First, copy the .env.example file:

    cp .env.example .env

You'll then need to fill in the `DISCORD_TOKEN` field with the bot's discord token. `ADMIN_CHANNEL_ID`, `VICTOR_ROLE_ID` and `VICTOR_TEXT_CHANNEL_ID` can be filled with any value, but they need to be filled.

Then, install all required dependencies:

    pip install -r requirements.txt

Finally, run the bot with

    python main.py

You may also be interested in editing `src/config.py` for some hardcoded values.

## Module structure

- `cogs`: stores all the cogs aka commands for the bot. View logic should reside here.
- `src/context`: stores all "business logic", such as puzzle release logic. Ideally accompanied with unit tests.
- `src/db`: all file related to database structures, such as database schemas.
- `src/models`: class files, either as a dataclass or a Pydantic model.
- `src/queries`: all database queries.
- `src/utils`: helper and middleware functions.
- `tests`: unit tests and Pytest config.

## Testing

First, set up the database as instructed [here](#local-database-setup). Then simply run

    pytest

and it should work out of the box!

There's a helper file for seeding data into the database if you want to do some manual test:

    python -m src.db.seed

## Local database setup

Included in the repository is a dockercompose.yml file to help with setting up the database.
To start the local database, simply do:

    docker compose up postgres16

This will start a local database that runs on port 5432 and store its data in a local pg_data directory.
To connect to the docker database, do:

    docker exec -it postgres16 psql -U postgres -d puzzlehunt_bot

For future maintainer, since the infra we're currently using is Fly.io:

To run the schema on remote fly machine, open a tunnel with `fly proxy 5432:5432 -a puzzlehunt-bot-db`, then use `psql` with -f and -h flags (-h flags forces psql to use TCP/IP instead of UNIX sockets)
