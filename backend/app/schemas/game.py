from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class GameCreate(BaseModel):
    nba_game_id: str
    q1_start_seconds: Optional[float] = None
    q2_start_seconds: Optional[float] = None
    q3_start_seconds: Optional[float] = None
    q4_start_seconds: Optional[float] = None


class GameResponse(BaseModel):
    id: int
    user_id: int
    nba_game_id: str
    video_path: Optional[str] = None
    status: str
    q1_start_seconds: Optional[float] = None
    q2_start_seconds: Optional[float] = None
    q3_start_seconds: Optional[float] = None
    q4_start_seconds: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
