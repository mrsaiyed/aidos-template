import logging
import os
import re
import subprocess
from pathlib import Path

from app.utils.constants import (
    DEAD_BALL_RATIO,
    DEGRADED_WINDOW_MULTIPLIER,
    QUARTER_BREAK_SEARCH_SECONDS,
    REFINEMENT_WINDOW_SECONDS,
)
from app.utils.paths import get_game_upload_dir

logger = logging.getLogger(__name__)

Q1_TIP_OFF_SECOND = 28.0
Q1_CLOCK_START = 720.0  # 12:00 in seconds remaining


class RefinementService:

    def refine_moments(
        self,
        game_id: int,
        nba_game_id: str,
        moments: list,
        db,
    ) -> dict:
        upload_dir = get_game_upload_dir(nba_game_id)
        video_path = os.path.join(upload_dir, "full_game.mp4")
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")

        # Sort into true game order: period ascending, clock descending (most remaining = earliest)
        sorted_moments = sorted(
            moments,
            key=lambda m: (m.period, -self._parse_game_clock(m.game_clock)),
        )

        anchor_second = Q1_TIP_OFF_SECOND
        last_confirmed_second = Q1_TIP_OFF_SECOND
        last_confirmed_clock = Q1_CLOCK_START
        degraded = False
        last_period = 1

        confirmed = 0
        interpolated = 0

        for moment in sorted_moments:
            clock_remaining = self._parse_game_clock(moment.game_clock)

            # --- Compute search window ---
            if moment.period != last_period:
                # Quarter boundary: wide window ahead of last anchor
                search_start = anchor_second + 60
                search_end = anchor_second + QUARTER_BREAK_SEARCH_SECONDS
                degraded = False
                logger.info(
                    "Quarter boundary Q%d → Q%d, wide window [%ds, %ds]",
                    last_period, moment.period, search_start, search_end,
                )
            elif degraded:
                window = REFINEMENT_WINDOW_SECONDS * DEGRADED_WINDOW_MULTIPLIER
                search_start = max(0.0, anchor_second - window)
                search_end = anchor_second + window
                logger.info(
                    "Degraded window for %s [%ds, %ds]",
                    moment.player_name, search_start, search_end,
                )
            else:
                search_start = max(0.0, anchor_second - 15)
                search_end = anchor_second + REFINEMENT_WINDOW_SECONDS

            context = {
                "player": moment.player_name,
                "play_type": moment.event_subtype or moment.event_type,
                "description": moment.description or "",
                "score_before": moment.score_before or "",
                "score_after": moment.score_after or "",
                "period": moment.period,
                "clock": moment.game_clock,
            }

            logger.info(
                "Scanning %s Q%d %s [%ds–%ds]",
                moment.player_name, moment.period, moment.game_clock,
                search_start, search_end,
            )

            found_second = self._run_watch_scan(
                video_path, search_start, search_end, context
            )

            # One retry with 2× window on first NOT_FOUND
            if found_second is None:
                logger.info("NOT_FOUND on first scan, retrying with wider window")
                found_second = self._run_watch_scan(
                    video_path,
                    max(0.0, search_start - REFINEMENT_WINDOW_SECONDS),
                    search_end + REFINEMENT_WINDOW_SECONDS,
                    context,
                )

            if found_second is not None:
                # CONFIRMED — advance both anchors
                moment.video_time_seconds = found_second
                moment.refinement_method = "watch_confirmed"
                moment.status = "refined"
                anchor_second = found_second
                last_confirmed_second = found_second
                last_confirmed_clock = clock_remaining
                degraded = False
                confirmed += 1
                logger.info(
                    "CONFIRMED %s at %.1fs", moment.player_name, found_second
                )
            else:
                # NOT_FOUND — interpolate from last confirmed anchor using clock gap
                # Errors do not compound: always derive from last_confirmed_second
                game_clock_elapsed = last_confirmed_clock - clock_remaining
                estimated_elapsed = game_clock_elapsed * DEAD_BALL_RATIO
                interpolated_second = last_confirmed_second + estimated_elapsed

                moment.video_time_seconds = interpolated_second
                moment.refinement_method = "interpolated"
                moment.status = "unconfirmed"
                anchor_second = interpolated_second
                degraded = True
                interpolated += 1
                logger.warning(
                    "NOT_FOUND %s — interpolated to %.1fs (clock gap %.1fs × %.1f)",
                    moment.player_name, interpolated_second,
                    game_clock_elapsed, DEAD_BALL_RATIO,
                )

            db.add(moment)
            db.commit()
            db.refresh(moment)

            last_period = moment.period

        return {
            "total": len(sorted_moments),
            "confirmed": confirmed,
            "interpolated": interpolated,
        }

    def _run_watch_scan(
        self,
        video_path: str,
        start_s: float,
        end_s: float,
        context: dict,
    ) -> float | None:
        start_mmss = self._seconds_to_mmss(start_s)
        end_mmss = self._seconds_to_mmss(end_s)

        prompt = (
            f"Q{context['period']} {context['clock']} remaining. "
            f"{context['player']} {context['play_type']}. "
            f"Score before: {context['score_before']}. "
            f"Score after: {context['score_after']}. "
            f"Find when score changes from {context['score_before']} "
            f"to {context['score_after']}. "
            f"Reply ONLY: FOUND: <seconds> or NOT_FOUND"
        )

        watch_script = Path.home() / ".claude" / "skills" / "watch" / "scripts" / "watch.py"
        if not watch_script.exists():
            logger.error("watch.py not found at %s", watch_script)
            return None

        try:
            result = subprocess.run(
                [
                    "python",
                    str(watch_script),
                    video_path,
                    "--start", start_mmss,
                    "--end", end_mmss,
                    "--no-whisper",
                    "--fps", "2",
                    "--resolution", "1024",
                    "--max-frames", "60",
                    "--question", prompt,
                ],
                capture_output=True,
                text=True,
                timeout=180,
            )
        except subprocess.TimeoutExpired:
            logger.warning("watch.py timed out for window [%s, %s]", start_mmss, end_mmss)
            return None
        except Exception as exc:
            logger.error("watch.py subprocess error: %s", exc)
            return None

        output = result.stdout + result.stderr
        match = re.search(r"FOUND:\s*(\d+(?:\.\d+)?)", output, re.IGNORECASE)
        if match:
            return float(match.group(1))
        return None

    def _seconds_to_mmss(self, seconds: float) -> str:
        total = int(max(0, seconds))
        m = total // 60
        s = total % 60
        return f"{m}:{s:02d}"

    def _parse_game_clock(self, clock: str) -> float:
        parts = clock.split(":")
        if len(parts) != 2:
            return 0.0
        try:
            return int(parts[0]) * 60 + float(parts[1])
        except ValueError:
            return 0.0
