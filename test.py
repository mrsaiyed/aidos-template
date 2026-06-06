import requests

BASE = "http://localhost:8000"
session = requests.Session()

print("=== REGISTER ===")
r = session.post(f"{BASE}/api/auth/register", json={
    "email": "test3@test.com",
    "username": "testuser3",
    "password": "password123"
})
print(r.json())

print("\n=== LOGIN ===")
r = session.post(f"{BASE}/api/auth/login", json={
    "email": "test@test.com",
    "password": "password123"
})
print(r.json())

print("\n=== ME ===")
r = session.get(f"{BASE}/api/auth/me")
print(r.json())

print("\n=== CREATE GAME ===")
r = session.post(f"{BASE}/api/games", json={
    "nba_game_id": "0052000121",
    "q1_start_seconds": 120.0
})
print(r.json())

print("\n=== LIST GAMES ===")
r = session.get(f"{BASE}/api/games")
print(r.json())
