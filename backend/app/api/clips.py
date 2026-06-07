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
from app.services.refinement_service import RefinementService
from app.utils.auth import get_current_user

router = APIRouter()


def _run_clip_generation(game_id: int, nba_game_id: str, moments: list, db: Session):
    clip_service = ClipService()
    clip_service.generate_clips(game_id, nba_game_id, moments, db)
    game = db.query(Game).filter(Game.id == game_id).first()
    if game:
        game.status = "cutting_clips"
        db.commit()


def _run_refinement(game_id: int, nba_game_id: str, moments: list, db: Session):
    refinement_service = RefinementService()
    refinement_service.refine_moments(game_id, nba_game_id, moments, db)
    game = db.query(Game).filter(Game.id == game_id).first()
    if game:
        game.status = "moments_refined"
        db.commit()


@router.post("/games/{game_id}/refine-moments")
def refine_moments(
    game_id: int,
    background_tasks: BackgroundTasks,
    team: Optional[str] = None,
    max_period: int = 4,
    highlight_type: str = "buckets",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    game = db.query(Game).filter(
        Game.id == game_id, Game.user_id == user.id
    ).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    query = db.query(Moment).filter(Moment.game_id == game_id)
    if team:
        query = query.filter(Moment.team == team)
    if highlight_type == "buckets":
        query = query.filter(Moment.event_type == "made_shot")
    query = query.filter(Moment.period <= max_period)
    moments = query.all()

    if not moments:
        raise HTTPException(
            status_code=400,
            detail="No matching moments found to refine.",
        )

    background_tasks.add_task(
        _run_refinement, game_id, game.nba_game_id, moments, db
    )

    return {
        "status": "processing",
        "message": "Moment refinement started in background",
        "moments_queued": len(moments),
        "filters": {
            "team": team,
            "highlight_type": highlight_type,
            "max_period": max_period,
        },
    }


@router.post("/games/{game_id}/generate-clips")
def generate_clips(
    game_id: int,
    background_tasks: BackgroundTasks,
    team: Optional[str] = None,
    highlight_type: str = "buckets",
    max_period: int = 4,
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
