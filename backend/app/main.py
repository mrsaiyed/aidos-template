from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.db.database import engine, Base
from app.models.user import User
from app.models.game import Game
from app.api.auth import router as auth_router
from app.api.games import router as games_router

app = FastAPI(title="NBA Highlight MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("data/outputs", exist_ok=True)
app.mount("/outputs", StaticFiles(directory="data/outputs"), name="outputs")

app.include_router(auth_router, prefix="/api/auth")
app.include_router(games_router, prefix="/api/games")


@app.get("/health")
def health():
    return {"status": "ok", "game_id": "0052000121"}


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    print("NBA Highlight MVP backend starting...")
