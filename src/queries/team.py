import psycopg
from psycopg.rows import class_row
from datetime import datetime

from src.config import config
from src.models.team import Team

DATABASE_URL = config["DATABASE_URL"]


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
                INSERT INTO public.teams
                (team_name, category_channel_id, voice_channel_id, text_channel_id, team_role_id)
                AS
                VALUES(%s, %s, %s, %s, %s)
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
    aconn = await psycopg.AsyncConnection.connect(DATABASE_URL)
    acur = await aconn.cursor(row_factor=class_row(Team))

    await acur.execute(
        """
        SELECT * FROM public.teams as t
        WHERE t.team_name = %s
        """,
        (team_name,),
    )

    result = await acur.fetchone()
    aconn.close()

    return result
