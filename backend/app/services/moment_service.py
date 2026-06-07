from app.models.moment import Moment


class MomentService:
    HIGHLIGHT_RULES = {
        "three_pointer": 80,
        "dunk": 90,
        "block": 85,
        "steal": 75,
        "layup": 40,
        "jump_shot": 30,
    }

    MINIMUM_IMPORTANCE = 70

    def process_events(
        self,
        events: list[dict],
        game_id: int,
        db,
        mode: str = "buckets",
    ) -> list:
        moments = []
        for event in events:
            if not self.is_highlight_worthy(event, mode=mode):
                continue
            score = self.score_event(event)
            moment = Moment(
                game_id=game_id,
                player_name=event["player_name"],
                team=event.get("team"),
                event_type=event["event_type"],
                event_subtype=event.get("event_subtype"),
                period=event["period"],
                game_clock=event["game_clock"],
                importance_score=score,
                status="pending",
            )
            db.add(moment)
            moments.append(moment)
        db.commit()
        for moment in moments:
            db.refresh(moment)
        return moments

    def is_highlight_worthy(
        self,
        event: dict,
        mode: str = "highlights",
    ) -> bool:
        event_type = event.get("event_type")
        event_subtype = event.get("event_subtype")

        if mode == "buckets":
            return event_type == "made_shot"

        if event_type == "made_shot" and event_subtype in ["three_pointer", "dunk"]:
            return True
        if event_type in ["block", "steal"]:
            return True
        if self._is_clutch_score(event):
            return True
        return False

    def score_event(self, event: dict) -> int:
        event_type = event.get("event_type")
        event_subtype = event.get("event_subtype")

        if event_type in ["block", "steal"]:
            base_score = self.HIGHLIGHT_RULES.get(event_subtype or event_type, 0)
            if event_subtype is None:
                base_score = self.HIGHLIGHT_RULES.get(event_type, 0)
        else:
            base_score = self.HIGHLIGHT_RULES.get(event_subtype, 0)

        if self._is_clutch_score(event):
            base_score += 20

        return min(base_score, 100)

    def _is_clutch_score(self, event: dict) -> bool:
        if event.get("period") != 4:
            return False
        if event.get("event_type") != "made_shot":
            return False
        minutes = self._parse_clock_minutes(event.get("game_clock", "12:00"))
        return minutes <= 2

    def _parse_clock_minutes(self, game_clock: str) -> int:
        parts = game_clock.split(":")
        return int(parts[0])
