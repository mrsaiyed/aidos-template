# Phase 4: FFmpeg Clip Cutting

## Goal
Cut individual video clips around each highlight moment using FFmpeg.

## Status
Complete

## Inputs
- Phase 3 moments with video_time_seconds populated
- Full game video at backend/data/uploads/{nba_game_id}/full_game.mp4

## Outputs
- Clip model and clips table in SQLite
- ffmpeg.py utility (cut_clip, get_video_duration, concatenate_clips)
- ClipService with bounds calculation and top-moment selection
- POST /api/games/{game_id}/generate-clips endpoint
- GET /api/games/{game_id}/clips endpoint
- Individual MP4 clips in outputs/{nba_game_id}/clips/{player}/
- test_clip_service.py with 5 unit tests

## Tasks
- [x] TASK 1: Create Clip model
- [x] TASK 2: Update main.py
- [x] TASK 3: Create ffmpeg utility
- [x] TASK 4: Create clip_service.py
- [x] TASK 5: Create clips API endpoint
- [x] TASK 6: Create test_clip_service.py
- [x] TASK 7: Test full clip generation (test_phase4.py)
- [x] TASK 8: Verify clips on disk
- [x] TASK 9: Update documentation

## Acceptance Criteria
- calculate_clip_bounds clamps to video start/end
- Top moments per player selected by importance_score descending
- MAX_CLIPS_PER_PLAYER limits clips per player
- FFmpeg cuts playable MP4 clips to player folders
- Clip records stored in SQLite with file paths and status
- All 26 unit tests pass

## Decisions Made
- FFmpeg uses libx264 + aac for compatibility
- Clips clamped to video bounds using calculate_clip_bounds
- MAX_CLIPS_PER_PLAYER = 5 keeps demo fast
- Top moments selected by importance_score descending
- File paths stored in DB not video blobs
- All paths go through paths.py
- Moments with video_time beyond actual video duration are marked failed
- Real Q1 start timestamp: 34 seconds (0:34 in video)
- Q1 end: 1308 seconds (21:48 in video)
- Scoped to Q1 only for MVP demo
- Team filter: LAL only
- Highlight type: buckets (made_shot) only
- Skipped status added for out-of-bounds moments
- generate-clips endpoint accepts team, highlight_type, max_period query params
- Clip generation runs as FastAPI BackgroundTask so API returns immediately
