from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base


class Clip(Base):
    __tablename__ = "clips"

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False, index=True)
    moment_id = Column(Integer, ForeignKey("moments.id"), nullable=False)
    player_name = Column(String, nullable=False)
    start_seconds = Column(Float, nullable=False)
    end_seconds = Column(Float, nullable=False)
    duration_seconds = Column(Float, nullable=False)
    file_path = Column(String, nullable=True)
    # Valid statuses: pending, generated, failed, skipped
    status = Column(String, default="pending")
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
