from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.game import Game
from app.models.moment import Moment
from app.models.user import User
from app.schemas.moment import MomentResponse, FetchMomentsResponse
from app.services.nba_service import NBAService
from app.services.moment_service import MomentService
from app.utils.auth import get_current_user

router = APIRouter()


@router.get("/games/{game_id}/moments", response_model=list[MomentResponse])
def list_moments(
    game_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    game = db.query(Game).filter(Game.id == game_id, Game.user_id == user.id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return db.query(Moment).filter(Moment.game_id == game_id).all()


@router.post("/games/{game_id}/fetch-moments", response_model=FetchMomentsResponse)
def fetch_moments(
    game_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    game = db.query(Game).filter(Game.id == game_id, Game.user_id == user.id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    nba_service = NBAService()
    moment_service = MomentService()

    events = nba_service.fetch_play_by_play(game.nba_game_id)
    moments = moment_service.process_events(events, game.id, db)

    game.status = "creating_moments"
    db.commit()

    return FetchMomentsResponse(count=len(moments), moments=moments)
