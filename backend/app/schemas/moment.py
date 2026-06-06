from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MomentResponse(BaseModel):
    id: int
    game_id: int
    player_name: str
    team: Optional[str] = None
    event_type: str
    event_subtype: Optional[str] = None
    period: int
    game_clock: str
    video_time_seconds: Optional[float] = None
    importance_score: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class FetchMomentsResponse(BaseModel):
    count: int
    moments: list[MomentResponse]
