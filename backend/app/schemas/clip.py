from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ClipResponse(BaseModel):
    id: int
    game_id: int
    moment_id: int
    player_name: str
    start_seconds: float
    end_seconds: float
    duration_seconds: float
    file_path: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class GenerateClipsResponse(BaseModel):
    total_clips_attempted: int
    successful: int
    failed: int
    players: list[str]
