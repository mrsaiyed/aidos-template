from app.services.timeline_service import TimelineService
import pytest

service = TimelineService()

Q1 = 120.0
Q2 = 2300.0
Q3 = 4600.0
Q4 = 6900.0

def test_parse_clock_standard():
    assert service.parse_game_clock("10:30") == 630.0

def test_parse_clock_under_one_minute():
    assert service.parse_game_clock("0:58") == 58.0

def test_parse_clock_full_quarter():
    assert service.parse_game_clock("12:00") == 720.0

def test_parse_clock_zero():
    assert service.parse_game_clock("0:00") == 0.0

def test_parse_clock_invalid_raises():
    with pytest.raises(ValueError):
        service.parse_game_clock("invalid")

def test_q1_event_timing():
    # Q1 10:30 remaining = 1:30 elapsed = 90 seconds in
    # video_time = Q1_start + 90 = 120 + 90 = 210
    result = service.calculate_video_time(1, "10:30", Q1, Q2, Q3, Q4)
    assert result == 210.0

def test_q2_event_timing():
    # Q2 6:00 remaining = 6:00 elapsed = 360 seconds in
    # video_time = Q2_start + 360 = 2300 + 360 = 2660
    result = service.calculate_video_time(2, "6:00", Q1, Q2, Q3, Q4)
    assert result == 2660.0

def test_q3_event_timing():
    # Q3 6:00 remaining = 6:00 elapsed = 360 seconds
    # video_time = Q3_start + 360 = 4600 + 360 = 4960
    result = service.calculate_video_time(3, "6:00", Q1, Q2, Q3, Q4)
    assert result == 4960.0

def test_q4_lebron_clutch_three():
    # Q4 0:58 remaining = 11:02 elapsed = 662 seconds
    # video_time = Q4_start + 662 = 6900 + 662 = 7562
    result = service.calculate_video_time(4, "0:58", Q1, Q2, Q3, Q4)
    assert result == 7562.0

def test_invalid_period_raises():
    with pytest.raises(ValueError):
        service.get_quarter_start(0, Q1, Q2, Q3, Q4)

def test_video_time_never_negative():
    result = service.calculate_video_time(1, "12:00", Q1, Q2, Q3, Q4)
    assert result >= 0.0
