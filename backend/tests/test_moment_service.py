import pytest
from app.services.moment_service import MomentService

service = MomentService()

def test_three_pointer_is_highlight_worthy():
    event = {
        "event_type": "made_shot",
        "event_subtype": "three_pointer",
        "period": 2,
        "game_clock": "8:00"
    }
    assert service.is_highlight_worthy(event) is True

def test_dunk_is_highlight_worthy():
    event = {
        "event_type": "made_shot",
        "event_subtype": "dunk",
        "period": 1,
        "game_clock": "10:00"
    }
    assert service.is_highlight_worthy(event) is True

def test_layup_is_not_highlight_worthy():
    event = {
        "event_type": "made_shot",
        "event_subtype": "layup",
        "period": 1,
        "game_clock": "10:00"
    }
    assert service.is_highlight_worthy(event) is False

def test_block_is_highlight_worthy():
    event = {
        "event_type": "block",
        "event_subtype": None,
        "period": 2,
        "game_clock": "5:00"
    }
    assert service.is_highlight_worthy(event) is True

def test_steal_is_highlight_worthy():
    event = {
        "event_type": "steal",
        "event_subtype": None,
        "period": 3,
        "game_clock": "7:00"
    }
    assert service.is_highlight_worthy(event) is True

def test_clutch_shot_is_highlight_worthy():
    event = {
        "event_type": "made_shot",
        "event_subtype": "jump_shot",
        "period": 4,
        "game_clock": "1:30"
    }
    assert service.is_highlight_worthy(event) is True

def test_score_three_pointer():
    event = {
        "event_type": "made_shot",
        "event_subtype": "three_pointer",
        "period": 2,
        "game_clock": "8:00"
    }
    assert service.score_event(event) == 80

def test_score_clutch_bonus():
    event = {
        "event_type": "made_shot",
        "event_subtype": "three_pointer",
        "period": 4,
        "game_clock": "1:00"
    }
    score = service.score_event(event)
    assert score == 100

def test_score_dunk():
    event = {
        "event_type": "made_shot",
        "event_subtype": "dunk",
        "period": 1,
        "game_clock": "10:00"
    }
    assert service.score_event(event) == 90

def test_process_events_creates_moments(db, mock_events):
    from app.models.game import Game
    from app.models.user import User
    import datetime
    
    user = User(
        email="test@test.com",
        username="testuser",
        password_hash="fakehash",
        created_at=datetime.datetime.utcnow()
    )
    db.add(user)
    db.flush()
    
    game = Game(
        user_id=user.id,
        nba_game_id="0052000121",
        status="created",
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow()
    )
    db.add(game)
    db.flush()
    
    moments = service.process_events(mock_events, game.id, db)
    highlight_events = [e for e in mock_events 
                       if service.is_highlight_worthy(e)]
    assert len(moments) == len(highlight_events)
