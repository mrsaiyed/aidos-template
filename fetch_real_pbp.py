import json
import os
import re
from nba_api.stats.endpoints import PlayByPlayV3

GAME_ID = "0052000121"


def clock_to_pctimestring(clock: str) -> str:
    """Convert PT11M37.00S -> 11:37"""
    match = re.match(r"PT(\d+)M([\d.]+)S", clock)
    if not match:
        return clock
    minutes = int(match.group(1))
    seconds = int(float(match.group(2)))
    return f"{minutes}:{seconds:02d}"


print(f"Fetching real play-by-play for game {GAME_ID}...")
print("This may take 10-30 seconds...")

try:
    pbp = PlayByPlayV3(game_id=GAME_ID)
    df = pbp.get_data_frames()[0]

    # Q1 only
    df = df[df["period"] == 1].copy()

    print(f"Total events fetched: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    made_shots = df[(df["shotResult"] == "Made") & (df["isFieldGoal"] == 1)]
    print(f"\nMade shots in Q1: {len(made_shots)}")

    print("\nQ1 made shots:")
    for _, row in made_shots.iterrows():
        player = row["playerName"]
        clock = clock_to_pctimestring(row["clock"])
        desc = row["description"]
        print(f"  {player} | {clock} | {desc}")

    records = df.to_dict("records")

    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "backend", "data", "mock", "real_play_by_play.json"
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(records, f, indent=2, default=str)

    print(f"\nSaved to {output_path}")
    print("Done.")

except Exception as e:
    print(f"Error: {e}")
    print("NBA API may be blocked. Try again or use a VPN.")
