import requests

BASE = "http://localhost:8000"
session = requests.Session()

print("=== LOGIN ===")
r = session.post(f"{BASE}/api/auth/login", json={
    "email": "test3@test.com",
    "password": "password123"
})
print(r.status_code)

print("\n=== FETCH MOMENTS FROM REAL DATA ===")
r = session.post(f"{BASE}/api/games/1/fetch-moments")
print(r.status_code, r.json())

print("\n=== MAP TIMELINE ===")
r = session.post(f"{BASE}/api/games/1/map-timeline")
print(r.status_code, r.json())

print("\n=== Q1 LAKERS MOMENTS ===")
r = session.get(f"{BASE}/api/games/1/moments")
moments = r.json()
lal_q1 = [m for m in moments
          if m['period'] == 1 and m['team'] == 'LAL']
print(f"Lakers Q1 moments: {len(lal_q1)}")
for m in lal_q1:
    print(f"  {m['player_name']} | {m['game_clock']} | "
          f"video_time={m['video_time_seconds']}s | "
          f"type={m['event_subtype']}")
