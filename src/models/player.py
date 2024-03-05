from pydantic import BaseModel


class Player(BaseModel):
    discord_id: int
    team_name: str
