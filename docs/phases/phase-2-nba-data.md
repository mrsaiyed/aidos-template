# Phase 2: NBA Data + Moments

## Goal
Fetch play-by-play for game 0052000121 and extract highlight moments
with importance scoring.

## Status
Complete

## Inputs
- Phase 1 backend with games table and auth
- NBA Game ID 0052000121 (Warriors vs Lakers, May 19 2021)

## Outputs
- Moment model and moments table in SQLite
- NBAService with nba_api fetch and mock JSON fallback
- MomentService with highlight filtering and importance scoring
- GET /api/games/{game_id}/moments endpoint
- POST /api/games/{game_id}/fetch-moments endpoint
- Mock play-by-play JSON at backend/data/mock/play_by_play_sample.json

## Tasks
- [x] TASK 1: Create Moment model
- [x] TASK 2: Import Moment in main.py for table creation
- [x] TASK 3: Create mock play-by-play data
- [x] TASK 4: Create nba_service.py
- [x] TASK 5: Create moment_service.py
- [x] TASK 6: Create moments API endpoint
- [x] TASK 7: Register moments router in main.py
- [x] TASK 8: Verify with test_phase2.py
- [x] TASK 9: Update documentation

## Acceptance Criteria
- POST /api/games/{id}/fetch-moments populates moments table
- GET /api/games/{id}/moments returns highlight moments for the game
- Mock fallback works when nba_api is unavailable
- 14 highlight moments extracted from mock data for game 0052000121

## Decisions Made
- nba_api primary with mock fallback for reliable offline demo
- importance scores drive clip priority in later phases
- minimum score of 70 filters low value plays (reserved for future use)
- mock JSON used for reliable demo when API is down
- Unit tests added alongside moment_service
- constants.py created as single source of truth for all magic numbers — all services must import from here
- pytest must pass before every git push
- conftest.py provides shared test fixtures for all future tests
- mock_events fixture in conftest.py is the standard test dataset for all pipeline tests going forward
- Real NBA API schema differs from mock schema. normalize_event() handles both formats automatically. Real clock format PT11M23.00S parsed to MM:SS.
- Buckets mode captures ALL made shots regardless of importance score. Highlights mode uses score threshold. Mode passed at API level — pipeline is filter-agnostic. This supports the full vision: every bucket gets clipped.

## Highlight Rules and Scores

| Event Subtype / Type | Base Score |
|---------------------|------------|
| three_pointer       | 80         |
| dunk                | 90         |
| block               | 85         |
| steal               | 75         |
| layup               | 40         |
| jump_shot           | 30         |

**Highlight-worthy criteria:**
- Made shot with subtype three_pointer or dunk
- Block or steal events
- Clutch made shot in Q4 with game clock ≤ 2:00

**Clutch bonus:** +20 in Q4 with clock ≤ 2:00 (max score capped at 100)

**Minimum importance threshold:** 70 (for future filtering)
