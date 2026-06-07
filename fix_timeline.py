import sys
import os

os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, '.')

# Import all models so SQLAlchemy can resolve all FK references
from app.models.user import User  # noqa: F401
from app.models.game import Game  # noqa: F401
from app.models.moment import Moment
from app.models.clip import Clip  # noqa: F401
from app.db.database import SessionLocal
from app.services.timeline_service import TimelineService

db = SessionLocal()
service = TimelineService()

moments = db.query(Moment).filter(
    Moment.game_id == 1,
    Moment.period == 1
).all()

print(f"Remapping {len(moments)} Q1 moments...")

for m in moments:
    video_time = service.calculate_video_time(
        period=m.period,
        game_clock=m.game_clock,
        q1_start=34.0,
        q2_start=9999.0,
        q3_start=9999.0,
        q4_start=9999.0
    )
    m.video_time_seconds = video_time
    m.status = "mapped"
    print(f"  {m.player_name} | Q{m.period} {m.game_clock} "
          f"-> video second {video_time:.1f}")

db.commit()
db.close()
print("Done.")
