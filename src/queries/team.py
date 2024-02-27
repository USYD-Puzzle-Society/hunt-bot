import psycopg
from psycopg.rows import class_row
from datetime import datetime

from src.config import config
from src.models.team import Team
from src.models.player import Player

DATABASE_URL = config["DATABASE_URL"]


async def get_team(team_name: str):
    aconn = await psycopg.AsyncConnection.connect(DATABASE_URL)
    acur = aconn.cursor(row_factory=class_row(Team))

    await acur.execute(
        """
        SELECT * FROM public.teams as t
        WHERE t.team_name = %s
        """,
        (team_name,),
    )

    # there should only be one result
    result = await acur.fetchone()
    acur.close()
    aconn.close()

    return result


async def get_team_members(team_name: str):
    aconn = await psycopg.AsyncConnection.connect(DATABASE_URL)
    acur = aconn.cursor(row_factory=class_row(Player))

    await acur.execute(
        """
        SELECT * FROM public.players AS t
        JOIN public.teams AS p
        WHERE t.team_name = p.team_name
        """
    )

    players = await acur.fetchall()

    acur.close()
    aconn.close()

    return players


async def create_team(
    team_name: str,
    category_channel_id: str,
    voice_channel_id: str,
    text_channel_id: str,
    team_role_id: str,
):
    aconn = await psycopg.AsyncConnection.connect(DATABASE_URL)
    acur = aconn.cursor()

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

    aconn.commit()
    acur.close()
    aconn.close()


async def remove_team(team_name: str):
    aconn = await psycopg.AsyncConnection.connect(DATABASE_URL)
    acur = aconn.cursor(row_factory=class_row(Team))

    # check existence of team
    if not await get_team(team_name):
        return False

    # team exists otherwise
    await acur.execute(
        """
        DELETE FROM public.teams 
        WHERE t.team_name = %s
        """,
        (team_name,),
    )

    aconn.commit()
    acur.close()
    aconn.close()