import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.game import Game
from app.models.user import User
from app.schemas.game import GameCreate, GameResponse
from app.utils.auth import get_current_user
from app.utils.paths import get_game_upload_dir

router = APIRouter()


@router.post("", response_model=GameResponse)
def create_game(
    body: GameCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    game = Game(
        user_id=user.id,
        nba_game_id=body.nba_game_id,
        q1_start_seconds=body.q1_start_seconds,
        q2_start_seconds=body.q2_start_seconds,
        q3_start_seconds=body.q3_start_seconds,
        q4_start_seconds=body.q4_start_seconds,
        status="created",
    )
    db.add(game)
    db.commit()
    db.refresh(game)
    return game


@router.get("", response_model=list[GameResponse])
def list_games(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Game).filter(Game.user_id == user.id).all()


@router.get("/{game_id}", response_model=GameResponse)
def get_game(
    game_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    game = db.query(Game).filter(Game.id == game_id, Game.user_id == user.id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@router.post("/{game_id}/upload", response_model=GameResponse)
def upload_game_video(
    game_id: int,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    game = db.query(Game).filter(Game.id == game_id, Game.user_id == user.id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    upload_dir = get_game_upload_dir(game.nba_game_id)
    file_path = os.path.join(upload_dir, "full_game.mp4")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    game.video_path = file_path
    db.commit()
    db.refresh(game)
    return game
