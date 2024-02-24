# hunt bot

## Local database setup

Included in the repository is a dockercompose.yml file to help with setting up the database.
To start the local database, simply do:

    docker compose up postgres16

This will start a local database that runs on port 5432 and store its data in a local pg_data directory.
To connect to the docker database, do:

    docker exec -it postgres16 psql -U postgres

For future maintainer, since the infra we're curerntly using is Fly.io:
To run the schema on remote fly machine, open a tunnel with `fly proxy`, then use `psql` with -f and -h flags (-h flags forces psql to use TCP/IP instead of UNIX sockets)
