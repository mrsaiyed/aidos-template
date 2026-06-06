import requests

BASE = "http://localhost:8000"
session = requests.Session()

print("=== LOGIN ===")
r = session.post(f"{BASE}/api/auth/login", json={
    "email": "test3@test.com",
    "password": "password123"
})
print(r.status_code, r.json())

print("\n=== MAP TIMELINE ===")
r = session.post(f"{BASE}/api/games/1/map-timeline")
print(r.status_code, r.json())

print("\n=== CHECK MOMENTS HAVE VIDEO TIMES ===")
r = session.get(f"{BASE}/api/games/1/moments")
moments = r.json()
print(f"Total moments: {len(moments)}")
print("First 5 with video times:")
for m in moments[:5]:
    print(f"  {m['player_name']} | {m['game_clock']} | "
          f"video_time={m['video_time_seconds']}s | "
          f"period={m['period']}")
