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

## Pipeline Services

| Service | File | Responsibility |
|---------|------|----------------|
| NBAService | `nba_service.py` | Fetch play-by-play from nba_api with mock JSON fallback |
| MomentService | `moment_service.py` | Filter highlight-worthy events and assign importance scores |
| TimelineService | `timeline_service.py` | Convert period + game clock to video timestamp in seconds |

### Timeline Formula

```
clock_remaining = parse_game_clock(game_clock)       # "MM:SS" → seconds remaining
elapsed_in_period = QUARTER_DURATION_SECONDS - clock_remaining
quarter_start = get_quarter_start(period, q1..q4)
video_time = max(0.0, quarter_start + elapsed_in_period)
```

**Quarter start lookup:**
- Period 1–4 → q1_start through q4_start
- Period 5+ → q4_start + QUARTER_DURATION_SECONDS + (period - 5) × OVERTIME_DURATION_SECONDS

**Example:** Q4 clock 0:58 with q4_start=6900 → elapsed=662s → video_time=7562.0

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
- test_timeline_service.py — game clock parsing and video time calculation
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
- MAX_CLIPS_PER_PLAYER = 5
