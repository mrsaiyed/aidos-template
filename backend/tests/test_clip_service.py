from app.services.clip_service import ClipService
import pytest

service = ClipService()


def test_calculate_clip_bounds_normal():
    start, end = service.calculate_clip_bounds(100.0, 7200.0)
    assert start == 93.0
    assert end == 101.0


def test_calculate_clip_bounds_clamps_start():
    start, end = service.calculate_clip_bounds(3.0, 7200.0)
    assert start == 0.0
    assert end == 4.0


def test_calculate_clip_bounds_clamps_end():
    start, end = service.calculate_clip_bounds(7199.5, 7200.0)
    assert start == 7192.5
    assert end == 7200.0


def test_get_top_moments_per_player(mock_events):
    from app.models.moment import Moment
    moments = []
    for i, e in enumerate(mock_events):
        m = Moment()
        m.id = i + 1
        m.player_name = e["player_name"]
        m.importance_score = e.get("importance_score", 50)
        m.video_time_seconds = 100.0 + i * 50
        m.game_clock = e["game_clock"]
        m.period = e["period"]
        m.event_type = e["event_type"]
        m.event_subtype = e.get("event_subtype")
        moments.append(m)

    result = service.get_top_moments_per_player(moments, max_per_player=2)

    players = {}
    for m in result:
        players[m.player_name] = players.get(m.player_name, 0) + 1

    for player, count in players.items():
        assert count <= 2


def test_get_top_moments_sorted_by_importance(mock_events):
    from app.models.moment import Moment
    moments = []
    scores = [90, 50, 80, 30, 85, 40]
    for i, e in enumerate(mock_events):
        m = Moment()
        m.id = i + 1
        m.player_name = "LeBron James"
        m.importance_score = scores[i]
        m.video_time_seconds = 100.0 + i * 50
        m.game_clock = e["game_clock"]
        m.period = e["period"]
        m.event_type = e["event_type"]
        m.event_subtype = e.get("event_subtype")
        moments.append(m)

    result = service.get_top_moments_per_player(moments, max_per_player=3)
    result_scores = [m.importance_score for m in result]
    assert result_scores == sorted(result_scores, reverse=True)
