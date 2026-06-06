# Phase 1: Backend + Database + Auth

## Goal
Set up SQLAlchemy models, auth with bcrypt + JWT cookies, and
CRUD endpoints for users and games.

## Status
Complete

## Inputs
- Phase 0 environment setup
- FastAPI app skeleton with paths.py

## Outputs
- SQLAlchemy engine + session + Base in db/database.py
- User model (users table)
- Game model (games table)
- Auth utility (bcrypt hash, JWT tokens, get_current_user dependency)
- Auth API (register, login, logout, me)
- Games API (create, list, get, upload)
- Pydantic schemas for User and Game
- Environment config (SECRET_KEY, DATABASE_URL, etc.)
- Tables auto-created on startup

## Tasks
- [x] TASK 1: Database setup (db/database.py)
- [x] TASK 2: User model (models/user.py)
- [x] TASK 3: Game model (models/game.py)
- [x] TASK 4: Auth schemas and utilities (utils/auth.py, schemas/user.py)
- [x] TASK 5: Auth API endpoints (api/auth.py)
- [x] TASK 6: Games API endpoints (api/games.py)
- [x] TASK 7: Update main.py (routers, table creation on startup)
- [x] TASK 8: Game Pydantic schemas (schemas/game.py)
- [x] TASK 9: Environment config (utils/config.py)
- [x] TASK 10: Verify all endpoints work
- [x] TASK 11: Update documentation

## Acceptance Criteria
- POST /api/auth/register returns user JSON with id, email, username, created_at
- POST /api/auth/login sets session_token cookie and returns user JSON
- GET /api/auth/me returns current user JSON when cookie is present
- POST /api/games creates a game record with status "created"
- GET /api/games returns list of games for authenticated user

## Problems Hit
- SQLite does not support `func.utcnow()` — switched to `func.now()`
- python-jose requires JWT `sub` claim to be a string — casting user_id to str

## Decisions Made
- bcrypt for password hashing (bcrypt >= 5.0.0)
- JWT in httponly cookie with 24-hour expiry (python-jose[cryptography])
- SQLAlchemy with autoincrement Integer primary keys
- Game video upload saves to paths.get_game_upload_dir(game.nba_game_id)/full_game.mp4
- Tables auto-created via Base.metadata.create_all() on startup
- SECRET_KEY defaults to "dev-secret-change-in-prod" when env var not set
