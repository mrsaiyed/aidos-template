import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.models.user import User
from app.models.game import Game
from app.models.moment import Moment

TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="function")
def db():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
def mock_events():
    return [
        {
            "player_name": "LeBron James",
            "team": "LAL",
            "event_type": "made_shot",
            "event_subtype": "three_pointer",
            "period": 4,
            "game_clock": "0:58",
            "description": "LeBron James 3PT Jump Shot"
        },
        {
            "player_name": "Anthony Davis",
            "team": "LAL",
            "event_type": "made_shot",
            "event_subtype": "dunk",
            "period": 2,
            "game_clock": "8:14",
            "description": "Anthony Davis Dunk"
        },
        {
            "player_name": "Stephen Curry",
            "team": "GSW",
            "event_type": "made_shot",
            "event_subtype": "three_pointer",
            "period": 3,
            "game_clock": "4:22",
            "description": "Stephen Curry 3PT Jump Shot"
        },
        {
            "player_name": "Draymond Green",
            "team": "GSW",
            "event_type": "steal",
            "event_subtype": None,
            "period": 1,
            "game_clock": "6:30",
            "description": "Draymond Green Steal"
        },
        {
            "player_name": "Anthony Davis",
            "team": "LAL",
            "event_type": "block",
            "event_subtype": None,
            "period": 2,
            "game_clock": "3:15",
            "description": "Anthony Davis Block"
        },
        {
            "player_name": "Dennis Schroder",
            "team": "LAL",
            "event_type": "made_shot",
            "event_subtype": "layup",
            "period": 1,
            "game_clock": "9:45",
            "description": "Dennis Schroder Layup"
        }
    ]
