import requests

BASE = "http://localhost:8000"
session = requests.Session()

print("=== LOGIN ===")
r = session.post(f"{BASE}/api/auth/login", json={
    "email": "test3@test.com",
    "password": "password123"
})
print(r.status_code, r.json())

print("\n=== FETCH MOMENTS ===")
r = session.post(f"{BASE}/api/games/1/fetch-moments")
print(r.status_code, r.json())

print("\n=== LIST MOMENTS ===")
r = session.get(f"{BASE}/api/games/1/moments")
data = r.json()
print(f"Total moments: {len(data)}")
if len(data) > 0:
    print("First 3 moments:")
    for m in data[:3]:
        print(m)
