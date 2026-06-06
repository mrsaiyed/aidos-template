import re

from app.utils.constants import OVERTIME_DURATION_SECONDS, QUARTER_DURATION_SECONDS


class TimelineService:
    def parse_game_clock(self, clock: str) -> float:
        if not re.match(r"^\d{1,2}:\d{2}$", clock):
            raise ValueError(f"Invalid game clock format: {clock}")

        minutes_str, seconds_str = clock.split(":")
        minutes = int(minutes_str)
        seconds = int(seconds_str)

        if seconds < 0 or seconds >= 60:
            raise ValueError(f"Invalid game clock format: {clock}")

        return float(minutes * 60 + seconds)

    def calculate_video_time(
        self,
        period: int,
        game_clock: str,
        q1_start: float,
        q2_start: float,
        q3_start: float,
        q4_start: float,
    ) -> float:
        clock_remaining = self.parse_game_clock(game_clock)
        elapsed_in_period = QUARTER_DURATION_SECONDS - clock_remaining
        quarter_start = self.get_quarter_start(period, q1_start, q2_start, q3_start, q4_start)
        video_time = quarter_start + elapsed_in_period
        return max(0.0, video_time)

    def get_quarter_start(
        self,
        period: int,
        q1_start: float,
        q2_start: float,
        q3_start: float,
        q4_start: float,
    ) -> float:
        if period < 1:
            raise ValueError(f"Invalid period: {period}")

        if period == 1:
            return q1_start
        if period == 2:
            return q2_start
        if period == 3:
            return q3_start
        if period == 4:
            return q4_start

        ot_periods_before = period - 5
        return (
            q4_start
            + QUARTER_DURATION_SECONDS
            + ot_periods_before * OVERTIME_DURATION_SECONDS
        )

    def map_moments_to_video(
        self,
        moments: list,
        q1_start: float,
        q2_start: float,
        q3_start: float,
        q4_start: float,
        db,
    ) -> list:
        for moment in moments:
            moment.video_time_seconds = self.calculate_video_time(
                moment.period,
                moment.game_clock,
                q1_start,
                q2_start,
                q3_start,
                q4_start,
            )
            moment.status = "mapped"

        db.commit()
        return moments
