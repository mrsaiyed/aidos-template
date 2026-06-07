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
Local pipeline: NBA game ID + uploaded video
→ team selector + player selector
→ player-specific highlight clips → view per player in browser.
No YouTube upload. No cloud storage. No OAuth. NBA only.
MVP scope: one game, one team, buckets only.
All other reel types and time periods are post-MVP.
Architecture already supports them — just needs frontend filters and multi-game processing.

**Hackathon MVP Frontend (Phase 7):**
- Upload full game video + enter NBA game ID
- Choose team (LAL or GSW from the upload)
- Select players to clip (multi-select or "Full team — all scorers")
- Trigger pipeline (fetch moments → refine moments → generate clips)
- View generated clips per player in the browser
- No approve/reject flow in hackathon MVP — just view and download

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
Phase 5B: Q2–Q4 Pipeline Extension
Note: Phase 5A Q1 agent-driven run complete June 7 2026. Q2–Q4 runs are next, followed by Phase 6 (pipeline endpoint) and Phase 7 (hackathon MVP frontend).
Phase 1 auth built but confirmation deferred to Phase 7.

## What Is Working
- FastAPI backend serving on port 8000
- /health endpoint returns status + game_id
- SQLite database with User and Game tables (auto-created on startup)
- Auth: register, login (JWT in httponly cookie), logout, me
- Games API: create, list, get, upload video
- NBA play-by-play fetch with mock fallback
- Moment extraction with importance scoring (score_before, score_after stored on each moment)
- moments table in SQLite with refinement_method and status columns
- Timeline mapping converts game clock to video timestamp (formula — drifts; replaced by anchor chain)
- FFmpeg clip cutting working (8s clips: 7s pre-roll, 1s post-roll)
- Clip records stored in SQLite with file paths
- RefinementService built with sequential anchor chain logic
- POST /api/games/{id}/refine-moments endpoint (BackgroundTask)
- Q1 hard cap removed — clips now generated for all 4 quarters
- **3-clip watch test complete (June 2026):** confirmed exact video timestamps for 3 Q1 Lakers plays:
  - Drummond dunk → 82s, KCP 3PT → 442s, Davis floater → 1177s
- **Q1 agent-driven run complete (June 7, 2026):** all 7 LAL scoring plays confirmed via watch.py frame analysis:
  - Drummond (82s), LeBron (258s), KCP ×2 (442s, 687s), Caruso ×2 (752s, 947s), AD (1176s)
  - 7 clips generated across 5 player folders; each exactly 8s, correctly centered on the score change
  - Self-correcting anchor chain validated: zero NOT_FOUND across all 7 plays; max drift 4s from anchor

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
- CLIP_PRE_ROLL_SECONDS = 7, CLIP_POST_ROLL_SECONDS = 1, CLIP_TOTAL_SECONDS = 8 (calibrated June 7 2026 from Q1 agent run — shot scores at exactly second 7 of the 8s clip, crowd reaction visible in post-roll second).
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
