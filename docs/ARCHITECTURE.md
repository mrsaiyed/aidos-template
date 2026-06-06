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
