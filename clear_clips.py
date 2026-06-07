import sys
import os

os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, '.')

from app.models.user import User  # noqa: F401
from app.models.game import Game  # noqa: F401
from app.models.moment import Moment  # noqa: F401
from app.db.database import SessionLocal
from app.models.clip import Clip
import shutil

db = SessionLocal()
db.query(Clip).filter(Clip.game_id == 1).delete()
db.commit()
db.close()

clips_dir = os.path.join(
    os.path.dirname(__file__), "backend", "data", "outputs", "0052000121", "clips"
)
if os.path.exists(clips_dir):
    shutil.rmtree(clips_dir)
    os.makedirs(clips_dir)
    print("Clips directory cleared.")

print("Clip records cleared.")
