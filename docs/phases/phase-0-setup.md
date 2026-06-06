# Phase 0: Environment Setup

## Goal
Confirm the Codespaces environment is ready and create the project
scaffold so every future phase has the right folders, config, and tooling.

## Status
In Progress

## Inputs
- Hackathon Codespaces template repo

## Outputs
- Folder structure created
- .gitignore updated
- .env.example created
- FFmpeg confirmed installed
- yt-dlp confirmed installed
- Python backend initialized with uv
- FastAPI app skeleton running at /health
- paths.py utility created
- All documentation files created

## Tasks
- [ ] Create folder structure
- [ ] Update .gitignore
- [ ] Create .env.example
- [ ] Confirm FFmpeg installed
- [ ] Confirm yt-dlp installed
- [ ] Initialize Python project with uv
- [ ] Create backend/app/main.py
- [ ] Create backend/app/utils/paths.py
- [ ] Create docs/PROJECT.md
- [ ] Create docs/ARCHITECTURE.md
- [ ] Create docs/PHASES.md
- [ ] Create docs/phases/phase-0-setup.md
- [ ] Test: GET /health returns 200

## Acceptance Criteria
- ffmpeg -version runs without error
- yt-dlp --version runs without error
- cd backend && uvicorn app.main:app --reload starts without error
- GET /health returns {"status": "ok", "game_id": "0052000121"}
- No MP4 or video files tracked by Git

## Problems Hit
(fill in during execution)

## Decisions Made
(fill in during execution)
