from unittest.mock import MagicMock, patch

import pytest

from app.services.refinement_service import RefinementService, Q1_TIP_OFF_SECOND, Q1_CLOCK_START
from app.utils.constants import (
    DEAD_BALL_RATIO,
    REFINEMENT_WINDOW_SECONDS,
    DEGRADED_WINDOW_MULTIPLIER,
    QUARTER_BREAK_SEARCH_SECONDS,
)


def _make_moment(player, period, clock, score_before="LAL 0 GSW 0", score_after="LAL 2 GSW 0"):
    m = MagicMock()
    m.player_name = player
    m.period = period
    m.game_clock = clock
    m.description = f"{player} made shot"
    m.score_before = score_before
    m.score_after = score_after
    m.event_type = "made_shot"
    m.event_subtype = "jump_shot"
    m.video_time_seconds = None
    m.refinement_method = None
    m.status = "pending"
    return m


@pytest.fixture
def service():
    return RefinementService()


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    return db


# ---------------------------------------------------------------------------
# _seconds_to_mmss
# ---------------------------------------------------------------------------

def test_seconds_to_mmss_whole(service):
    assert service._seconds_to_mmss(90.0) == "1:30"


def test_seconds_to_mmss_zero(service):
    assert service._seconds_to_mmss(0.0) == "0:00"


def test_seconds_to_mmss_clamps_negative(service):
    assert service._seconds_to_mmss(-5.0) == "0:00"


# ---------------------------------------------------------------------------
# _parse_game_clock
# ---------------------------------------------------------------------------

def test_parse_clock_standard(service):
    assert service._parse_game_clock("11:10") == pytest.approx(670.0)


def test_parse_clock_zero(service):
    assert service._parse_game_clock("0:00") == pytest.approx(0.0)


def test_parse_clock_bad_format(service):
    assert service._parse_game_clock("bad") == 0.0


# ---------------------------------------------------------------------------
# Anchor chain logic
# ---------------------------------------------------------------------------

def test_confirmed_play_advances_both_anchors(service, mock_db):
    """A FOUND result advances anchor_second and last_confirmed_second."""
    moment = _make_moment("LeBron James", 1, "11:00", "LAL 0 GSW 2", "LAL 2 GSW 2")

    with patch.object(service, "_run_watch_scan", return_value=82.0) as mock_scan:
        with patch("os.path.exists", return_value=True):
            result = service.refine_moments(1, "0052000121", [moment], mock_db)

    assert moment.video_time_seconds == 82.0
    assert moment.refinement_method == "watch_confirmed"
    assert moment.status == "refined"
    assert result["confirmed"] == 1
    assert result["interpolated"] == 0


def test_not_found_interpolates_from_last_confirmed(service, mock_db):
    """NOT_FOUND uses last_confirmed_second + clock_gap * DEAD_BALL_RATIO."""
    # First play confirmed at 82s with clock 11:10 (670s remaining)
    m1 = _make_moment("Drummond", 1, "11:10", "LAL 0 GSW 2", "LAL 2 GSW 2")
    # Second play NOT_FOUND; clock 6:40 (400s remaining); gap = 670 - 400 = 270s
    m2 = _make_moment("KCP", 1, "6:40", "LAL 4 GSW 9", "LAL 7 GSW 9")

    scan_calls = [82.0, None, None]  # first confirmed, retry 1 = None, retry 2 = None

    with patch.object(service, "_run_watch_scan", side_effect=scan_calls):
        with patch("os.path.exists", return_value=True):
            result = service.refine_moments(1, "0052000121", [m1, m2], mock_db)

    assert m1.refinement_method == "watch_confirmed"
    assert m2.refinement_method == "interpolated"
    assert m2.status == "unconfirmed"

    expected_elapsed = (670.0 - 400.0) * DEAD_BALL_RATIO
    expected_second = 82.0 + expected_elapsed
    assert m2.video_time_seconds == pytest.approx(expected_second, abs=0.1)
    assert result["interpolated"] == 1


def test_consecutive_not_found_both_use_same_last_confirmed(service, mock_db):
    """Two consecutive NOT_FOUND plays both derive from last_confirmed_second, not each other."""
    m1 = _make_moment("Drummond", 1, "11:10", "LAL 0 GSW 2", "LAL 2 GSW 2")
    # m1 confirmed at 82s, clock 670s remaining
    m2 = _make_moment("KCP", 1, "6:40", "LAL 4 GSW 9", "LAL 7 GSW 9")
    # m2 NOT_FOUND; gap from m1 anchor = 670 - 400 = 270s
    m3 = _make_moment("Davis", 1, "0:55", "LAL 12 GSW 15", "LAL 14 GSW 15")
    # m3 NOT_FOUND; gap from last_confirmed (still m1: 82s at clock 670s) = 670 - 55 = 615s

    # m1 confirmed (call 1), m2 NOT_FOUND (calls 2+3), m3 NOT_FOUND (calls 4+5)
    scan_returns = [82.0, None, None, None, None]

    with patch.object(service, "_run_watch_scan", side_effect=scan_returns):
        with patch("os.path.exists", return_value=True):
            service.refine_moments(1, "0052000121", [m1, m2, m3], mock_db)

    # m2: 82 + (670 - 400) * 1.6 = 82 + 432 = 514
    expected_m2 = 82.0 + (670.0 - 400.0) * DEAD_BALL_RATIO
    # m3: 82 + (670 - 55) * 1.6 = 82 + 984 = 1066
    # Both derive from last_confirmed_second=82, last_confirmed_clock=670
    expected_m3 = 82.0 + (670.0 - 55.0) * DEAD_BALL_RATIO

    assert m2.video_time_seconds == pytest.approx(expected_m2, abs=0.1)
    assert m3.video_time_seconds == pytest.approx(expected_m3, abs=0.1)
    assert m2.refinement_method == "interpolated"
    assert m3.refinement_method == "interpolated"


def test_degraded_flag_set_after_not_found(service, mock_db):
    """degraded=True is set after NOT_FOUND and clears after FOUND."""
    m1 = _make_moment("KCP", 1, "6:40")  # NOT_FOUND
    m2 = _make_moment("Davis", 1, "0:55")  # FOUND

    # m1: scan + retry = None, None; m2: scan = 1177.0
    scan_returns = [None, None, 1177.0]

    degraded_states = []

    original_scan = service._run_watch_scan

    call_count = [0]

    def tracking_scan(video_path, start_s, end_s, context):
        call_count[0] += 1
        return scan_returns[call_count[0] - 1]

    with patch.object(service, "_run_watch_scan", side_effect=tracking_scan):
        with patch("os.path.exists", return_value=True):
            service.refine_moments(1, "0052000121", [m1, m2], mock_db)

    assert m1.refinement_method == "interpolated"
    assert m2.refinement_method == "watch_confirmed"


def test_quarter_boundary_uses_wide_window(service, mock_db):
    """On period change, search window starts at anchor+60 and spans QUARTER_BREAK_SEARCH_SECONDS."""
    m1 = _make_moment("Drummond", 1, "0:30")   # last Q1 play
    m2 = _make_moment("LeBron", 2, "11:45")    # first Q2 play — quarter boundary

    scan_calls = []

    def capture_scan(video_path, start_s, end_s, context):
        scan_calls.append((start_s, end_s, context["period"]))
        if context["period"] == 2:
            return 1500.0
        return 100.0

    with patch.object(service, "_run_watch_scan", side_effect=capture_scan):
        with patch("os.path.exists", return_value=True):
            service.refine_moments(1, "0052000121", [m1, m2], mock_db)

    # Find the Q2 scan call
    q2_calls = [(s, e) for s, e, p in scan_calls if p == 2]
    assert len(q2_calls) >= 1
    start_s, end_s = q2_calls[0]
    # Window should be large (quarter break window)
    assert (end_s - start_s) == pytest.approx(QUARTER_BREAK_SEARCH_SECONDS - 60, abs=5)
