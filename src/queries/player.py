import psycopg
from psycopg.rows import class_row

from src.config import config
from src.models.player import Player

DATABASE_URL = config["DATABASE_URL"]


async def get_player(discord_id: str):
    aconn = await psycopg.AsyncConnection.connect(DATABASE_URL)
    acur = aconn.cursor(row_factory=class_row(Player))

    await acur.execute(
        """
        SELECT * FROM public.players AS p
        WHERE p.discord_id = %s
        """,
        (discord_id,),
    )

    player = await acur.fetchone()

    await aconn.close()
    await acur.close()

    return player


async def add_player(discord_id: str, team_name: str):
    aconn = await psycopg.AsyncConnection.connect(DATABASE_URL)
    acur = aconn.cursor()

    await acur.execute(
        """
        INSERT INTO public.players 
        (discord_id, team_name)
        VALUES (%s, %s)
        """,
        (discord_id, team_name),
    )

    await aconn.commit()

    await acur.close()
    await aconn.close()


async def remove_player(discord_id: str):
    aconn = await psycopg.AsyncConnection.connect(DATABASE_URL)
    acur = aconn.cursor()

    await acur.execute(
        """
        DELETE FROM public.players AS p
        WHERE p.discord_id = %s
        """,
        (discord_id,),
    )

    await aconn.commit()

    await acur.close()
    await aconn.close()
