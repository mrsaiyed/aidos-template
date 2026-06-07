import requests

s = requests.Session()
s.post("http://localhost:8000/api/auth/login",
       json={"email": "test3@test.com", "password": "password123"})

r = s.post("http://localhost:8000/api/games/1/fetch-moments?mode=buckets")
print("FETCH:", r.status_code, "count=", r.json()["count"])

r = s.post("http://localhost:8000/api/games/1/map-timeline")
print("MAP:", r.status_code, "count=", r.json()["count"])

moments = s.get("http://localhost:8000/api/games/1/moments").json()
lal_q1 = sorted(
    [m for m in moments if m["period"] == 1 and m["team"] == "LAL"],
    key=lambda m: m["game_clock"],
    reverse=True,
)
print(f"\nLakers Q1 moments: {len(lal_q1)}")
for m in lal_q1:
    print(f"  {m['player_name']:15s} | {m['game_clock']:5s} | "
          f"video_time={m['video_time_seconds']}s | "
          f"subtype={m['event_subtype']} | score={m['importance_score']}")
