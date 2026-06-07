# Phase 7: Hackathon MVP Frontend

## Goal
Build a minimal Next.js frontend that lets a user go from raw game video to per-player
highlight clips in a single browser session. No login required for the demo.

## MVP User Flow (5-minute demo target)

```
1. Upload page
   → drag/drop or file-pick the full_game.mp4
   → type in the NBA game ID (e.g. 0052000121)
   → hit "Load"
   
2. Team + player selection
   → choose team: LAL or GSW
   → player list auto-populates from NBA API play-by-play
   → pick individual players OR "Full team — all scorers"
   → choose clip type: Buckets (MVP), 3-Pointers, Dunks (post-MVP)
   → hit "Generate Clips"

3. Processing status
   → live polling every 2s: "Fetching moments... Refining timestamps... Cutting clips..."
   → simple progress bar or step indicator

4. Clips viewer
   → tabs across the top: one per player
   → each tab shows that player's clips in a grid
   → click any clip to play it inline (HTML5 video element)
   → clips served from FastAPI /outputs static files
```

## Status
Not started. Depends on Phase 6 (pipeline endpoint) and Phase 5B (Q2–Q4 clips ready).

## Tech Stack
- Framework: Next.js (App Router)
- Language: TypeScript
- Styling: Tailwind CSS
- HTTP client: fetch (no extra library needed for MVP)
- Video: native HTML5 `<video>` element
- State: React useState / useEffect (no Redux)
- Backend: existing FastAPI on port 8000

## Folder Structure
```
frontend/
  app/
    page.tsx              ← Upload + game ID entry
    [gameId]/
      setup/page.tsx      ← Team + player selection
      processing/page.tsx ← Live status polling
      clips/page.tsx      ← Clips viewer by player
  components/
    PlayerTabs.tsx
    ClipGrid.tsx
    ClipPlayer.tsx
    StatusStepper.tsx
  lib/
    api.ts               ← fetch wrappers for backend endpoints
```

## Backend Endpoints Required

All endpoints already exist or will be in Phase 6:

| Endpoint | Used for |
|----------|----------|
| `POST /api/games/` | Create game record, get game_id |
| `POST /api/games/{id}/upload` | Upload the video file |
| `POST /api/games/{id}/fetch-moments?team=LAL` | Pull NBA play-by-play |
| `POST /api/games/{id}/refine-moments?team=LAL&max_period=4` | Run anchor chain |
| `POST /api/games/{id}/generate-clips?team=LAL&max_period=4` | Cut FFmpeg clips |
| `GET /api/games/{id}` | Poll pipeline status |
| `GET /api/games/{id}/moments?team=LAL` | Get list of players with moments |
| `GET /api/games/{id}/clips?player=LeBron_James` | Get clips for one player |
| `GET /outputs/{game_id}/Q1_clips/{player}/{clip}.mp4` | Serve video file |

Phase 6 wraps the three pipeline steps (fetch → refine → clip) into one:
`POST /api/games/{id}/process?team=LAL&players=all&period=4`

## Key Decisions
- No login for hackathon demo — cookie auth deferred to post-MVP
- Players populated dynamically from NBA API, not hardcoded
- "Full team" = all players who scored at least once in the game
- Clips served directly from FastAPI static files — no separate CDN
- Processing runs as BackgroundTask; frontend polls every 2s
- Failure state shows which step failed and an error message
- Mobile-responsive is nice-to-have; desktop-first for hackathon

## Acceptance Criteria
- Upload video → enter game ID → choose team → choose players → see clips
- Full flow completes in under 5 minutes on a local machine
- Each player tab shows their clips in playable video elements
- No crashes on happy path (failure states handled gracefully)
- Works on Chrome/Edge desktop

## Tasks

### Phase 6 prerequisite: unified pipeline endpoint
- [ ] `POST /api/games/{id}/process` triggers fetch → refine → clip as one BackgroundTask
- [ ] Game status updates: `pending → fetching → refining → clipping → done | failed`
- [ ] Returns job_id; frontend polls `GET /api/games/{id}` for status

### Phase 7 frontend
- [ ] Scaffold Next.js app with Tailwind in `frontend/`
- [ ] Upload page: video file picker + game ID input + "Load" button
- [ ] `POST /api/games/` then `POST /api/games/{id}/upload` on submit
- [ ] Team selector: two buttons (LAL / GSW), selected team highlighted
- [ ] Player list: fetch from `GET /api/games/{id}/moments?team=LAL` after load
- [ ] Player multi-select with "Select all" toggle
- [ ] "Generate Clips" triggers `POST /api/games/{id}/process`
- [ ] Processing page: 2s polling loop, step display (Fetching / Refining / Clipping / Done)
- [ ] Redirect to clips page on `status=done`
- [ ] Clips page: player tabs + clip grid
- [ ] Each clip card: thumbnail (first frame) + play button → inline video modal
- [ ] Basic dark theme, clean typography
- [ ] Test end-to-end on game 0052000121 before demo

## Next Steps After Phase 7 (post-hackathon)
- Full approve/reject review flow (original Phase 7 scope)
- Render concatenated highlight reel per player (Phase 5 render service)
- YouTube upload per reel
- Login + user accounts (Phase 1 auth already built)
- Multi-game support (loop over game IDs)
