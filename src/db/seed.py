import asyncio
import psycopg

from src.config import config
from src.models.puzzle import Puzzle


DATABASE_URL = config["DATABASE_URL"]


async def seed_puzzles():
    sample_puzzles = [
        Puzzle("UTS-01", "UTS Puz1", "uts1", "skelly", "tiny.cc/puz", "UTS"),
        Puzzle("UTS-02", "UTS Puz2", "uts2", "skelly", "tiny.cc/puz", "UTS"),
        Puzzle("UTS-03", "UTS Puz3", "uts3", "skelly", "tiny.cc/puz", "UTS"),
        Puzzle("UTS-04", "UTS Puz4", "uts4", "skelly", "tiny.cc/puz", "UTS"),
        Puzzle("UTS-M", "UTS PuzM", "utsm", "skelly", "tiny.cc/puz", "UTS"),
        Puzzle("USYD-01", "USYD Puz1", "usyd1", "simon", "tiny.cc/puz", "USYD"),
        Puzzle("USYD-02", "USYD Puz2", "usyd2", "simon", "tiny.cc/puz", "USYD"),
        Puzzle("USYD-03", "USYD Puz3", "usyd3", "simon", "tiny.cc/puz", "USYD"),
        Puzzle("USYD-04", "USYD Puz4", "usyd4", "simon", "tiny.cc/puz", "USYD"),
        Puzzle("USYD-05", "USYD Puz5", "usyd5", "simon", "tiny.cc/puz", "USYD"),
        Puzzle("USYD-06", "USYD Puz6", "usyd6", "simon", "tiny.cc/puz", "USYD"),
        Puzzle("USYD-M", "USYD PuzM", "usydm", "simon", "tiny.cc/puz", "USYD"),
        Puzzle("UNSW-01", "UNSW Puz1", "unsw1", "timothy", "tiny.cc/puz", "UNSW"),
        Puzzle("UNSW-02", "UNSW Puz2", "unsw2", "timothy", "tiny.cc/puz", "UNSW"),
        Puzzle("UNSW-03", "UNSW Puz3", "unsw3", "timothy", "tiny.cc/puz", "UNSW"),
        Puzzle("UNSW-04", "UNSW Puz4", "unsw4", "timothy", "tiny.cc/puz", "UNSW"),
        Puzzle("UNSW-M", "UNSW PuzM", "unswm", "timothy", "tiny.cc/puz", "UNSW"),
        Puzzle(
            "METAMETA", "Meta Meta", "youwin", "everyone <3", "tiny.cc/puz", "METAMETA"
        ),
    ]

    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as aconn:
        async with aconn.cursor() as acur:
            for puzzle in sample_puzzles:
                await acur.execute(
                    """
                    INSERT INTO public.puzzles
                    (puzzle_id, puzzle_name, puzzle_answer, puzzle_author, puzzle_link, uni)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT(puzzle_id) 
                    DO UPDATE SET 
                      puzzle_name = EXCLUDED.puzzle_name,
                      puzzle_answer = EXCLUDED.puzzle_answer,
                      puzzle_author = EXCLUDED.puzzle_author,
                      puzzle_link = EXCLUDED.puzzle_link,
                      uni = EXCLUDED.uni
                    """,
                    (
                        puzzle.puzzle_id,
                        puzzle.puzzle_name,
                        puzzle.puzzle_answer,
                        puzzle.puzzle_author,
                        puzzle.puzzle_link,
                        puzzle.uni,
                    ),
                )


if __name__ == "__main__":
    asyncio.run(seed_puzzles())
