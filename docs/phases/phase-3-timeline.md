# Phase 3: Timeline Mapping

## Goal
Convert NBA game clock + period into video timestamps for each moment.

## Status
Complete

## Inputs
- Phase 2 moments with period and game_clock
- Manual quarter start timestamps on the game record (q1–q4_start_seconds)

## Outputs
- TimelineService with clock parsing and video time calculation
- POST /api/games/{game_id}/map-timeline endpoint
- All moments updated with video_time_seconds and status "mapped"
- test_timeline_service.py with 11 unit tests

## Tasks
- [x] TASK 1: Create timeline_service.py
- [x] TASK 2: Create test_timeline_service.py
- [x] TASK 3: Add map-timeline endpoint
- [x] TASK 4: Run full test suite (21 passed)
- [x] TASK 5: Manual endpoint test with test_phase3.py
- [x] TASK 6: Update documentation

## Acceptance Criteria
- parse_game_clock("10:30") returns 630.0
- Q1 10:30 maps to Q1 start + 90s (210.0 with Q1=120)
- Q4 0:58 (LeBron clutch three) maps to Q4 start + 662s (7562.0 with Q4=6900)
- All 21 unit tests pass (Phase 2 + Phase 3)
- POST /api/games/{id}/map-timeline populates video_time_seconds on all moments
- Returns 400 if quarter timestamps not set

## Decisions Made
- Formula is elapsed = QUARTER_DURATION - clock_remaining, video_time = quarter_start + elapsed
- Overtime supported but not tested with real data yet
- Manual quarter timestamps used for MVP
- Auto-detection planned for Phase 8
- All constants imported from app.utils.constants (QUARTER_DURATION_SECONDS, OVERTIME_DURATION_SECONDS)

## Timeline Formula

```
clock_remaining = parse_game_clock(game_clock)
elapsed_in_period = QUARTER_DURATION_SECONDS - clock_remaining
quarter_start = get_quarter_start(period, q1, q2, q3, q4)
video_time = max(0.0, quarter_start + elapsed_in_period)
```

**Overtime (period 5+):**
- Base = q4_start + QUARTER_DURATION_SECONDS
- Each additional OT period adds OVERTIME_DURATION_SECONDS
