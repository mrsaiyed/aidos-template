import sys
import os

os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, '.')

from app.models.user import User  # noqa: F401
from app.models.game import Game
from app.models.moment import Moment
from app.models.clip import Clip
from app.db.database import SessionLocal

db = SessionLocal()

print("Clearing clips...")
db.query(Clip).filter(Clip.game_id == 1).delete()

print("Clearing moments...")
db.query(Moment).filter(Moment.game_id == 1).delete()

game = db.query(Game).filter(Game.id == 1).first()
game.status = "created"
db.commit()
db.close()
print("Done. Ready to re-fetch moments.")
