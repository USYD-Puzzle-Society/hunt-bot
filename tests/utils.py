import psycopg

from src.config import config

DATABASE_URL = config["DATABASE_URL"]


async def truncate():
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as aconn:
        async with aconn.cursor() as acur:
            await acur.execute("TRUNCATE public.teams CASCADE")
            await acur.execute("TRUNCATE public.puzzles CASCADE")
            await acur.execute("TRUNCATE public.submissions CASCADE")
            await acur.execute("TRUNCATE public.players CASCADE")
