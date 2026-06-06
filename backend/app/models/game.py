from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    nba_game_id = Column(String, nullable=False)
    video_path = Column(String, nullable=True)
    q1_start_seconds = Column(Float, nullable=True)
    q2_start_seconds = Column(Float, nullable=True)
    q3_start_seconds = Column(Float, nullable=True)
    q4_start_seconds = Column(Float, nullable=True)
    status = Column(String, default="created")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
