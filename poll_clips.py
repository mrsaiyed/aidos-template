import sys, os, time
os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, '.')

import requests

s = requests.Session()
s.post('http://localhost:8000/api/auth/login',
       json={'email': 'test3@test.com', 'password': 'password123'})

for i in range(30):
    clips = s.get('http://localhost:8000/api/games/1/clips').json()
    game  = s.get('http://localhost:8000/api/games/1').json()
    gen   = sum(1 for c in clips if c['status'] == 'generated')
    fail  = sum(1 for c in clips if c['status'] == 'failed')
    skip  = sum(1 for c in clips if c['status'] == 'skipped')
    status = game['status']
    print(f"[poll {i:02d}] game.status={status}  clips={len(clips)}  gen={gen}  fail={fail}  skip={skip}")
    if status == 'cutting_clips' and len(clips) > 0:
        break
    time.sleep(10)

print("\n=== FINAL CLIP LIST ===")
clips = s.get('http://localhost:8000/api/games/1/clips').json()
print(f"Total clips: {len(clips)}")
for c in clips:
    print(f"  {c['player_name']} | {c['start_seconds']}s-{c['end_seconds']}s | "
          f"status={c['status']} | ts={c.get('start_seconds','?')}")
