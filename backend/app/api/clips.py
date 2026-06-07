from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.clip import Clip
from app.models.game import Game
from app.models.moment import Moment
from app.models.user import User
from app.schemas.clip import ClipResponse
from app.services.clip_service import ClipService
from app.utils.auth import get_current_user

router = APIRouter()

Q1_END_SECONDS = 1308.0


def _run_clip_generation(game_id: int, nba_game_id: str, moments: list, db: Session):
    clip_service = ClipService()
    clip_service.generate_clips(game_id, nba_game_id, moments, db)
    game = db.query(Game).filter(Game.id == game_id).first()
    if game:
        game.status = "cutting_clips"
        db.commit()


@router.post("/games/{game_id}/generate-clips")
def generate_clips(
    game_id: int,
    background_tasks: BackgroundTasks,
    team: Optional[str] = None,
    highlight_type: str = "buckets",
    max_period: int = 1,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    game = db.query(Game).filter(
        Game.id == game_id, Game.user_id == user.id
    ).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    query = db.query(Moment).filter(
        Moment.game_id == game_id,
        Moment.video_time_seconds.isnot(None),
    )
    if team:
        query = query.filter(Moment.team == team)
    if highlight_type == "buckets":
        query = query.filter(Moment.event_type == "made_shot")
    query = query.filter(Moment.period <= max_period)
    moments = query.all()

    # Drop moments outside the valid video window
    moments = [
        m for m in moments
        if m.video_time_seconds is not None and m.video_time_seconds <= Q1_END_SECONDS
    ]

    if not moments:
        raise HTTPException(
            status_code=400,
            detail="No matching moments found after applying filters.",
        )

    background_tasks.add_task(
        _run_clip_generation, game_id, game.nba_game_id, moments, db
    )

    return {
        "status": "processing",
        "message": "Clip generation started in background",
        "filters": {
            "team": team,
            "highlight_type": highlight_type,
            "max_period": max_period,
        },
    }


@router.get("/games/{game_id}/clips", response_model=list[ClipResponse])
def list_clips(
    game_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    game = db.query(Game).filter(
        Game.id == game_id, Game.user_id == user.id
    ).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    return db.query(Clip).filter(Clip.game_id == game_id).all()
