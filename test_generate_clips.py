import requests
import time

BASE = "http://localhost:8000"
session = requests.Session()

print("=== LOGIN ===")
r = session.post(f"{BASE}/api/auth/login", json={
    "email": "test3@test.com",
    "password": "password123"
})
print(r.status_code)

print("\n=== GENERATE Q1 LAKERS BUCKETS ===")
r = session.post(
    f"{BASE}/api/games/1/generate-clips"
    f"?team=LAL&highlight_type=buckets&max_period=1"
)
print(r.status_code, r.json())

print("\nWaiting for clips to generate...")
for i in range(18):
    time.sleep(10)
    r = session.get(f"{BASE}/api/games/1")
    status = r.json().get("status")
    print(f"  {(i+1)*10}s — game status: {status}")
    if status in ["needs_review", "completed", "failed"]:
        break

print("\n=== CLIP RESULTS ===")
r = session.get(f"{BASE}/api/games/1/clips")
clips = r.json()
print(f"Total clips: {len(clips)}")
for c in clips:
    print(f"  {c['player_name']} | "
          f"{c['start_seconds']}s-{c['end_seconds']}s | "
          f"status={c['status']} | "
          f"size will be checked on disk")
