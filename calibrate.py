import sys
import os

os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, '.')

from app.services.timeline_service import TimelineService

service = TimelineService()

q1_start = 30.0

events = [
    ("Wiggins first layup", 1, "11:23"),
    ("Drummond dunk", 1, "11:10"),
    ("Bazemore three", 1, "10:55"),
    ("Wiggins step back", 1, "10:21"),
    ("Looney jump shot", 1, "9:35"),
    ("LeBron tip layup", 1, "8:29"),
    ("Bazemore second three", 1, "8:18"),
    ("Wiggins third shot", 1, "7:38"),
    ("KCP first three", 1, "6:40"),
    ("Curry floater", 1, "4:59"),
    ("KCP second three", 1, "4:43"),
    ("Caruso three", 1, "4:13"),
    ("Caruso layup", 1, "2:49"),
    ("Mulder dunk", 1, "1:49"),
    ("Curry layup", 1, "1:02"),
    ("Davis floater", 1, "0:55"),
    ("Toscano three", 1, "0:46"),
]

print(f"Q1 start assumed: {q1_start}s")
print(f"{'Event':<25} {'Clock':<8} {'Video Time':<12} {'MM:SS'}")
print("-" * 60)
for name, period, clock in events:
    vt = service.calculate_video_time(period, clock, q1_start, 9999, 9999, 9999)
    mins = int(vt // 60)
    secs = int(vt % 60)
    print(f"{name:<25} {clock:<8} {vt:<12.1f} {mins}:{secs:02d}")
