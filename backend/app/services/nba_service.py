import json
import os

from app.utils.paths import MOCK_DIR

EVENT_TYPE_MAP = {
    1: "made_shot",
    2: "missed_shot",
    3: "free_throw",
    4: "rebound",
    5: "turnover",
    6: "foul",
    10: "jump_ball",
    12: "start_period",
    13: "end_period",
}


class NBAService:
    def fetch_play_by_play(self, nba_game_id: str) -> list[dict]:
        try:
            from nba_api.stats.endpoints import playbyplayv2

            pbp = playbyplayv2.PlayByPlayV2(game_id=nba_game_id)
            df = pbp.get_data_frames()[0]
            events = df.to_dict(orient="records")
            return [self.normalize_event(event) for event in events]
        except Exception:
            return [self.normalize_event(event) for event in self.load_mock_play_by_play()]

    def load_mock_play_by_play(self) -> list[dict]:
        path = os.path.join(MOCK_DIR, "play_by_play_sample.json")
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def normalize_event(self, raw_event: dict) -> dict:
        if "EVENTMSGTYPE" in raw_event:
            return self._normalize_nba_api_event(raw_event)
        return self._normalize_mock_event(raw_event)

    def _normalize_nba_api_event(self, raw_event: dict) -> dict:
        event_type_num = raw_event.get("EVENTMSGTYPE")
        event_type = EVENT_TYPE_MAP.get(event_type_num, "other")

        home_desc = raw_event.get("HOMEDESCRIPTION") or ""
        visitor_desc = raw_event.get("VISITORDESCRIPTION") or ""
        description = home_desc or visitor_desc

        if event_type == "turnover" and "STEAL" in description.upper():
            event_type = "steal"
        elif event_type == "missed_shot" and "BLOCK" in description.upper():
            event_type = "block"

        event_subtype = None
        if event_type == "made_shot":
            event_subtype = self._detect_shot_subtype(description)

        player_name = raw_event.get("PLAYER1_NAME") or ""
        team = self._detect_team(home_desc, visitor_desc)

        period = int(raw_event.get("PERIOD", 0))
        game_clock = raw_event.get("PCTIMESTRING") or "12:00"

        return {
            "player_name": player_name,
            "team": team,
            "event_type": event_type,
            "event_subtype": event_subtype,
            "period": period,
            "game_clock": game_clock,
            "description": description,
        }

    def _normalize_mock_event(self, raw_event: dict) -> dict:
        event_type = raw_event.get("event_type", "other")
        description = raw_event.get("description", "")

        event_subtype = None
        if event_type == "made_shot":
            event_subtype = self._detect_shot_subtype(description)

        return {
            "player_name": raw_event.get("player_name", ""),
            "team": raw_event.get("team"),
            "event_type": event_type,
            "event_subtype": event_subtype,
            "period": int(raw_event.get("period", 0)),
            "game_clock": raw_event.get("clock", "12:00"),
            "description": description,
        }

    def _detect_shot_subtype(self, description: str) -> str | None:
        desc_upper = description.upper()
        if "3PT" in desc_upper or "THREE" in desc_upper:
            return "three_pointer"
        if "DUNK" in desc_upper:
            return "dunk"
        if "LAYUP" in desc_upper:
            return "layup"
        if "JUMP SHOT" in desc_upper:
            return "jump_shot"
        if "HOOK" in desc_upper:
            return "hook_shot"
        return None

    def _detect_team(self, home_desc: str, visitor_desc: str) -> str | None:
        if home_desc:
            return "LAL"
        if visitor_desc:
            return "GSW"
        return None
