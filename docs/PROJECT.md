# NBA Highlight MVP — Project Document

## North Star (Long Term Vision)

For any NBA team, for any player, for any time period:
generate separate highlight reels by play type.

Reel types:
  Buckets      — all made shots
  3-pointers   — three pointers only
  Dunks        — dunks only
  Layups       — layups only
  Assists      — all assists
  Blocks       — all blocks
  Steals       — all steals
  Misses       — missed shots (analytics)
  Custom       — any combination the user defines

Time period scope:
  Single game
  Week
  Month
  Season
  Career

Example use cases:
  "LeBron all 3s this season"
  "AD all dunks this month"
  "Curry all assists from last night"
  "Full Lakers buckets reel from last night"
  "Steph all misses Q4 this season" (analytics)

Pipeline supports this today because:
  event_type stored on every moment (made_shot, block, steal)
  event_subtype stored on every moment (three_pointer, dunk, layup)
  player_name and team stored on every moment
  game_id stored on every moment
  Filtering happens at API layer — no pipeline changes needed

What needs to be built for full vision:
  Multi-game processing (loop over game IDs)
  Season-long data storage
  User-defined filter combinations in frontend
  YouTube upload per reel
  Cloud storage per user account

## MVP North Star
Local pipeline: NBA game ID + uploaded video + quarter timestamps
→ player-specific highlight videos → review UI → approved output folder.
No YouTube upload. No cloud storage. No OAuth. NBA only.
MVP scope: one game, one team, buckets only.
All other reel types and time periods are post-MVP.
Architecture already supports them — just needs
frontend filters and multi-game processing.

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
Phase 5A: Full Game Pipeline — Self-Correcting Timestamp Refinement — NOT STARTED
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
- Timeline mapping converts game clock to video timestamp
- All 14 moments now have video_time_seconds populated
- LeBron clutch three maps to correct video second (7562.0s)
- FFmpeg clip cutting working
- Clips generated per player in output folders
- Clip records stored in SQLite with file paths
- Real Q1 timestamps confirmed: start=34s, end=1308s
- Lakers Q1 buckets only — correct scope for MVP demo
- **3-clip watch test complete (June 2026):** claude-video watch skill manually
  confirmed exact video timestamps for 3 Q1 Lakers plays using NBA API score context:
  - Drummond dunk → 82s (formula estimated 78s — 4s drift, acceptable)
  - KCP 3PT → 442s (formula estimated 348s — 94s drift, formula unusable)
  - Davis floater → 1177s (formula estimated 693s — 484s drift, formula unusable)
  This confirmed that NBA API score signatures (score_before / score_after) reliably
  identify the exact frame in a watch scan. Sequential anchor chain architecture validated.

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
- Timeline formula: elapsed = QUARTER_DURATION_SECONDS - clock_remaining, video_time = quarter_start + elapsed. Manual quarter timestamps for MVP; auto-detection in Phase 8.
- MAX_CLIPS_PER_PLAYER = 5 limits clips per player for fast demo; top moments selected by importance_score descending.
- Switched from mock play-by-play to real NBA API data. Real Q1 data confirmed: 17 total events, 6 Lakers buckets. Real API uses PT format for clock — normalized in nba_service. real_play_by_play.json saved for offline/demo fallback.
- Two processing modes: buckets = all made shots, no filtering by type; highlights = dunks, threes, blocks, steals, clutch only. MVP uses buckets mode for all clip generation.
- **3-clip watch test (June 2026):** formula-only timeline unusable beyond early Q1 due to dead-ball drift. Confirmed that NBA API score_before/score_after + claude-video watch scan reliably finds exact video second within ±5s.
- **Self-correcting anchor chain (Phase 5A decision):** each confirmed video timestamp becomes the new search anchor for the next play. No manual Q2/Q3/Q4 timestamps needed. Q1 hard cap removed. Phase 8 auto quarter detection superseded by this approach.
- CLIP_PRE_ROLL_SECONDS = 4, CLIP_POST_ROLL_SECONDS = 4, CLIP_TOTAL_SECONDS = 8 (updated June 2026 after watch test clip review).
- score_before and score_after will be stored as strings on Moment model (e.g. "LAL 4 GSW 15") and sourced from scoreHome/scoreAway fields already present in the raw NBA API response.
- refinement_method stored on each Moment: "watch_confirmed" | "interpolated" | "formula" to track data quality.

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
