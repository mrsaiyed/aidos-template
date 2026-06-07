import sys
import os

os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, '.')

# Import all models so SQLAlchemy can resolve all FK references
from app.models.user import User  # noqa: F401
from app.models.game import Game
from app.models.moment import Moment  # noqa: F401
from app.models.clip import Clip  # noqa: F401
from app.db.database import SessionLocal

db = SessionLocal()
game = db.query(Game).filter(Game.id == 1).first()
game.q1_start_seconds = 34.0
game.q2_start_seconds = None
game.q3_start_seconds = None
game.q4_start_seconds = None
db.commit()
print(f"Updated game {game.id}: q1_start={game.q1_start_seconds}")
db.close()
