import time
import requests

# Q1 only, Lakers only, buckets only
# Q1 start = 34 seconds
# Q1 end = 1308 seconds (21:48)
# All clip video_time_seconds should be between 34 and 1308

BASE = "http://localhost:8000"
session = requests.Session()

print("=== LOGIN ===")
r = session.post(f"{BASE}/api/auth/login", json={
    "email": "test3@test.com",
    "password": "password123"
})
print(r.status_code, r.json())

print("\n=== GENERATE CLIPS ===")
print("Filters: team=LAL, highlight_type=buckets, max_period=1")
r = session.post(
    f"{BASE}/api/games/1/generate-clips"
    "?team=LAL&highlight_type=buckets&max_period=1",
    timeout=30
)
print(r.status_code, r.json())

print("\n=== WAIT FOR BACKGROUND TASK ===")
for i in range(30):
    game = session.get(f"{BASE}/api/games/1").json()
    clips = session.get(f"{BASE}/api/games/1/clips").json()
    print(f"  poll {i}: game.status={game['status']}  clips={len(clips)}")
    if game["status"] == "cutting_clips" and len(clips) > 0:
        break
    time.sleep(10)

print("\n=== LIST CLIPS ===")
r = session.get(f"{BASE}/api/games/1/clips")
clips = r.json()
print(f"Total clips: {len(clips)}")
for c in clips:
    print(f"  {c['player_name']} | "
          f"{c['start_seconds']}s-{c['end_seconds']}s | "
          f"status={c['status']} | "
          f"path={c['file_path']}")
