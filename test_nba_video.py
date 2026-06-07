import requests
import json
from nba_api.stats.endpoints import videoevents

cdn_headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Origin': 'https://www.nba.com',
    'Referer': 'https://www.nba.com/',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
}

game_id = "0052000121"

print("Fetching play-by-play to get event IDs...")
pbp_url = f"https://cdn.nba.com/static/json/liveData/playbyplay/playbyplay_{game_id}.json"
r = requests.get(pbp_url, headers=cdn_headers)
print(f"Play-by-play status: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    actions = data['game']['actions']

    made_shots = [a for a in actions
                  if a.get('actionType') == 'Made Shot'
                  or (a.get('isFieldGoal') == 1
                      and a.get('shotResult') == 'Made')]

    print(f"Total made shots: {len(made_shots)}")

    if made_shots:
        first = made_shots[0]
        action_id = first.get('actionId') or first.get('actionNumber')
        print(f"\nFirst made shot:")
        print(f"  actionId: {action_id}")
        print(f"  player: {first.get('playerName')}")
        print(f"  clock: {first.get('clock')}")
        print(f"  description: {first.get('description')}")

        print(f"\nTrying VideoEvents endpoint...")
        try:
            ve = videoevents.VideoEvents(
                game_id=game_id,
                game_event_id=action_id
            )
            result = ve.nba_response.get_dict()
            print(f"VideoEvents response:")
            print(json.dumps(result, indent=2)[:2000])
        except Exception as e:
            print(f"VideoEvents error: {e}")

        print(f"\nTrying direct CDN URL pattern...")
        date = "2021/05/19"
        url = f"https://videos.nba.com/nba/pbp/media/{date}/{game_id}/{action_id}/"
        r2 = requests.get(url, headers=cdn_headers)
        print(f"CDN URL status: {r2.status_code}")
        print(f"URL tried: {url}")
else:
    print(f"Failed to fetch play-by-play: {r.text[:500]}")
