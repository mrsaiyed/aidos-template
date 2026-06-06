# NBA Highlight MVP — Project Document

## North Star (Long Term Vision)
Automatically clip NBA highlights from full game video or livestreams,
group highlights by player, classify as YouTube Short or normal video,
and upload to YouTube automatically.

Long term the system evolves in three layers:
- Layer 1 (MVP): Play-by-play API data identifies what happened, who did it,
  and when in the game clock. This gives us rich context — event type, score,
  clutch situations, assist relationships.
- Layer 2 (Post-MVP): Computer vision refines exact clip start/end frames and
  adds defensive highlights not captured in play-by-play data.
- Layer 3 (Future): Vision-only mode for non-NBA video with no structured API —
  college, international, street ball. Jersey detection, pose estimation.

The timestamp + play-by-play approach is not a dead end. It is Layer 1 of a
system that gets smarter. The SportAdapter pattern keeps NBA logic separate
from shared pipeline logic so other sports and vision modes can be added later.

## MVP North Star
Local pipeline: NBA game ID + uploaded video + quarter timestamps
→ player-specific highlight videos → review UI → approved output folder.
No YouTube upload. No cloud storage. No OAuth. NBA only.

## The Game We Are Using
- Teams: Golden State Warriors vs Los Angeles Lakers
- Date: May 19, 2021
- Context: Western Conference Play-In Tournament
- Result: Lakers win 103-100 (LeBron go-ahead 3 with 58s left)
- NBA Game ID: 0052000121

## Hard Rules (Never Break These)
- Never commit MP4 or video files to Git
- No YouTube upload in MVP
- No cloud storage in MVP
- No real OAuth in MVP (simple bcrypt login only)
- NBA only for now
- FFmpeg handles all video processing
- All file paths go through backend/app/utils/paths.py
- All pipeline results stored in SQLite

## Tech Stack
- Backend: FastAPI + Python 3.12
- Database: SQLite (via SQLAlchemy)
- Video processing: FFmpeg
- NBA data: nba_api library + mock JSON fallback
- Frontend: Next.js
- Auth: bcrypt + session token (cookie-based, simple)
- Environment: GitHub Codespaces
- AI coding: opencode + DeepSeek V4 Pro

## Current Phase
Phase 3: Timeline Mapping — IN PROGRESS
Note: Phase 1 auth built but confirmation deferred to Phase 7

## What Is Working
- FastAPI backend serving on port 8000
- /health endpoint returns status + game_id
- SQLite database with User and Game tables (auto-created on startup)
- Auth: register, login (JWT in httponly cookie), logout, me
- Games API: create, list, get, upload video
- NBA play-by-play fetch with mock fallback
- Moment extraction with importance scoring
- moments table in SQLite

## What Is Blocked
- Nothing yet

## Key Decisions Made
- Manual quarter timestamps for MVP, auto-detection added later
- Single sanitize_player_name function in paths.py used everywhere
- Static files served by FastAPI at /outputs for video preview
- Background tasks for pipeline so API does not time out
- Auth deprioritized — auth system built in Phase 1 but full confirmation deferred until frontend is ready in Phase 7. Core logic exists: register, login, logout, me endpoints all created. Confirmation blocked on PowerShell curl issues, not code issues.
- constants.py is the single source of truth for all pipeline numbers. If a number appears in more than one place it belongs in constants.py instead.
- conftest.py mock_events is the canonical test dataset. Any new test that needs play-by-play events uses this fixture.

## Documentation Rules
These docs are updated after every phase and every key decision.
No phase is marked complete without passing its acceptance criteria.
If a phase is deferred or partially complete it is marked as such.
ROADMAP.html status is updated in sync with PHASES.md.
- Unit tests written alongside every service
- Run pytest before every git push
- All tests must pass before a phase is marked complete
- Test files live in backend/tests/
- Constants live in backend/app/utils/constants.py

## Git Rules
- Push to main after every completed phase
- Always run git check-ignore on video files before committing
- Never commit files from backend/data/uploads/ or backend/data/outputs/
- Commit message format: "Phase N complete - one line summary"
- If a phase is partial, commit with: "Phase N partial - what is done"
- The video full_game.mp4 must never appear in git history
