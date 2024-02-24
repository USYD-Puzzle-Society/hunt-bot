import psycopg
from src.config import config
import asyncio

DATABASE_URL = config["DATABASE_URL"]


async def truncate():
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as aconn:
        async with aconn.cursor() as acur:
            await acur.execute("TRUNCATE public.teams CASCADE")


async def create_team(
    team_name: str,
    category_channel_id: str,
    voice_channel_id: str,
    text_channel_id: str,
    team_role_id: str,
):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as aconn:
        async with aconn.cursor() as acur:
            await acur.execute(
                """
                INSERT INTO public.teams (team_name, category_channel_id, voice_channel_id, text_channel_id, team_role_id) 
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    team_name,
                    category_channel_id,
                    voice_channel_id,
                    text_channel_id,
                    team_role_id,
                ),
            )


async def get_team(team_name: str):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as aconn:
        async with aconn.cursor() as acur:
            await acur.execute(
                "SELECT * from public.teams WHERE team_name = %s", (team_name,)
            )
            records = await acur.fetchall()
            return records


async def main():
    await truncate()
    await create_team("test", "boop1", "boop2", "boop3", "boop4")
    teams = await get_team("test")
    return teams


if __name__ == "__main__":
    asyncio.run(main())
