# Architecture

## Pipeline Flow
User creates game → uploads video → enters quarter timestamps
→ backend fetches NBA play-by-play for game 0052000121
→ moment service identifies highlight events
→ timeline service maps game clock to video timestamp
→ FFmpeg cuts individual clips per moment
→ clips grouped by player
→ FFmpeg renders one video per player
→ video classified as Short (≤2min) or Video (>2min)
→ frontend review page shows each player video
→ user approves or rejects
→ approved videos copied to approved/ folder

## Folder Structure
backend/data/uploads/{game_id}/          ← uploaded full game video
backend/data/outputs/{game_id}/clips/    ← individual moment clips by player
backend/data/outputs/{game_id}/rendered/ ← one compiled video per player
backend/data/outputs/{game_id}/approved/ ← approved final videos
backend/data/mock/                       ← mock play-by-play JSON fallback

## DB Schema (to be defined in Phase 1)
Tables: users, games, moments, clips, rendered_videos

## API Endpoints (to be defined in Phase 1)
See phase-1-backend.md when complete.

## Testing Architecture

All tests live in backend/tests/
Run with: cd backend && pytest tests/ -v

Test files:
- conftest.py — shared fixtures: test DB, mock_events dataset
- test_moment_service.py — moment extraction and scoring logic
- test_timeline_service.py — to be added in Phase 3
- test_clip_service.py — to be added in Phase 4
- test_render_service.py — to be added in Phase 5

Rules:
- Every service gets a corresponding test file
- All tests must pass before phase is marked complete
- All tests must pass before git push
- Use the shared mock_events fixture from conftest.py
- Use the shared db fixture for any database operations

## Constants

All magic numbers live in backend/app/utils/constants.py
No hardcoded numbers anywhere else in the codebase.

Current constants:
- QUARTER_DURATION_SECONDS = 720 (12 minutes)
- CLIP_PRE_ROLL_SECONDS = 8
- CLIP_POST_ROLL_SECONDS = 12
- SHORT_MAX_DURATION_SECONDS = 120
- MINIMUM_IMPORTANCE_SCORE = 70
- FRAME_SAMPLE_INTERVAL_SECONDS = 30
- NBA_QUARTERS = [1, 2, 3, 4]
- OVERTIME_DURATION_SECONDS = 300
