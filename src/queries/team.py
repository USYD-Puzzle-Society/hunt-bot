import psycopg
from psycopg.rows import class_row
from src.models.puzzle import Puzzle

from src.config import config
from src.models.team import Team
from src.models.player import Player

DATABASE_URL = config["DATABASE_URL"]


async def get_team(team_name: str):
    aconn = await psycopg.AsyncConnection.connect(DATABASE_URL)
    acur = aconn.cursor(row_factory=class_row(Team))

    await acur.execute(
        """
        SELECT * FROM public.teams AS t
        WHERE t.team_name = %s
        """,
        (team_name,),
    )

    # there should only be one result
    result = await acur.fetchone()
    await acur.close()
    await aconn.close()

    return result


async def get_team_members(team_name: str):
    aconn = await psycopg.AsyncConnection.connect(DATABASE_URL)
    acur = aconn.cursor(row_factory=class_row(Player))

    await acur.execute(
        """
        SELECT p.discord_id, p.team_name FROM public.players AS p
        JOIN public.teams AS t
        ON t.team_name = p.team_name
        WHERE t.team_name = %s
        """,
        (team_name,),
    )

    players = await acur.fetchall()

    await acur.close()
    await aconn.close()

    return players


async def create_team(
    team_name: str,
    category_channel_id: int,
    voice_channel_id: int,
    text_channel_id: int,
    team_role_id: int,
):
    aconn = await psycopg.AsyncConnection.connect(DATABASE_URL)
    acur = aconn.cursor()

    await acur.execute(
        """
        INSERT INTO public.teams
        (team_name, category_channel_id, voice_channel_id, text_channel_id, team_role_id)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            team_name,
            str(category_channel_id),
            str(voice_channel_id),
            str(text_channel_id),
            str(team_role_id),
        ),
    )

    await aconn.commit()
    await acur.close()
    await aconn.close()


async def remove_team(team_name: str):
    aconn = await psycopg.AsyncConnection.connect(DATABASE_URL)
    acur = aconn.cursor(row_factory=class_row(Team))

    # check existence of team
    if not await get_team(team_name):
        return False

    # team exists otherwise
    await acur.execute(
        """
        DELETE FROM public.teams AS t
        WHERE t.team_name = %s
        """,
        (team_name,),
    )

    await aconn.commit()
    await acur.close()
    await aconn.close()


async def increase_puzzles_solved(team_name: str):
    aconn = await psycopg.AsyncConnection.connect(DATABASE_URL)
    acur = aconn.cursor()

    # this should never run since the team name should always be
    # valid when calling this function
    if not await get_team(team_name):
        return False

    await acur.execute(
        """
        UPDATE public.teams
        SET puzzle_solved = puzzle_solved + 1
        WHERE team_name = %s
        """,
        (team_name,),
    )

    await aconn.commit()
    await acur.close()
    await aconn.close()


async def increase_hints_used(team_name: str):
    aconn = await psycopg.AsyncConnection.connect(DATABASE_URL)
    acur = aconn.cursor()

    if not await get_team(team_name):
        return False

    await acur.execute(
        """
        UPDATE public.teams
        SET hints_used = hints_used + 1
        WHERE team_name = %s
        """,
        (team_name,),
    )

    await aconn.commit()
    await acur.close()
    await aconn.close()
