from pydantic import BaseModel


class Team(BaseModel):
    team_name: str
    category_channel_id: int
    voice_channel_id: int
    text_channel_id: int
    team_role_id: int
    puzzle_solved: int
    hints_used: int
