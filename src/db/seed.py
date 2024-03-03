import asyncio
import psycopg

from src.config import config
from src.models.puzzle import Puzzle


DATABASE_URL = config["DATABASE_URL"]


async def seed_puzzles():
    sample_puzzles = [
        Puzzle("UTS-1", "UTS Puz1", "uts1", "skelly", "tiny.cc/puz", "UTS"),
        Puzzle("UTS-2", "UTS Puz2", "uts2", "skelly", "tiny.cc/puz", "UTS"),
        Puzzle("UTS-3", "UTS Puz3", "uts3", "skelly", "tiny.cc/puz", "UTS"),
        Puzzle("UTS-4", "UTS Puz4", "uts4", "skelly", "tiny.cc/puz", "UTS"),
        Puzzle("UTS-M", "UTS PuzM", "utsm", "skelly", "tiny.cc/puz", "UTS"),
        Puzzle("USYD-1", "USYD Puz1", "usyd1", "simon", "tiny.cc/puz", "USYD"),
        Puzzle("USYD-2", "USYD Puz2", "usyd2", "simon", "tiny.cc/puz", "USYD"),
        Puzzle("USYD-3", "USYD Puz3", "usyd3", "simon", "tiny.cc/puz", "USYD"),
        Puzzle("USYD-4", "USYD Puz4", "usyd4", "simon", "tiny.cc/puz", "USYD"),
        Puzzle("USYD-5", "USYD Puz5", "usyd5", "simon", "tiny.cc/puz", "USYD"),
        Puzzle("USYD-6", "USYD Puz6", "usyd6", "simon", "tiny.cc/puz", "USYD"),
        Puzzle("USYD-M", "USYD PuzM", "usydm", "simon", "tiny.cc/puz", "USYD"),
        Puzzle("UNSW-1", "UNSW Puz1", "unsw1", "timothy", "tiny.cc/puz", "UNSW"),
        Puzzle("UNSW-2", "UNSW Puz2", "unsw2", "timothy", "tiny.cc/puz", "UNSW"),
        Puzzle("UNSW-3", "UNSW Puz3", "unsw3", "timothy", "tiny.cc/puz", "UNSW"),
        Puzzle("UNSW-4", "UNSW Puz4", "unsw4", "timothy", "tiny.cc/puz", "UNSW"),
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
