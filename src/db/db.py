import psycopg
from src.config import config
import asyncio

DATABASE_URL = config["DATABASE_URL"]


async def truncate():
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as aconn:
        async with aconn.cursor() as acur:
            await acur.execute("TRUNCATE public.teams CASCADE")


async def create_team(team_name: str, team_channel_id: str):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as aconn:
        async with aconn.cursor() as acur:
            await acur.execute(
                "INSERT INTO public.teams (team_name, team_channel) VALUES (%s, %s)",
                (team_name, team_channel_id),
            )


async def get_team(team_name: str):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as aconn:
        async with aconn.cursor() as acur:
            await acur.execute(
                "SELECT * from public.teams WHERE team_name = %s", (team_name,)
            )
            records = await acur.fetchall()
            for record in records:
                print(record)


async def main():
    await truncate()
    await create_team("test", "boop")
    await get_team("test")


if __name__ == "__main__":
    asyncio.run(main())
