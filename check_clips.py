import os

clips_dir = os.path.join(
    os.path.dirname(__file__), "backend", "data", "outputs", "0052000121", "clips"
)
total_size = 0
for player in sorted(os.listdir(clips_dir)):
    player_dir = os.path.join(clips_dir, player)
    if not os.path.isdir(player_dir):
        continue
    clips = os.listdir(player_dir)
    print(f"\n{player}: {len(clips)} clip(s)")
    for clip in sorted(clips):
        path = os.path.join(player_dir, clip)
        size = os.path.getsize(path)
        total_size += size
        print(f"  {clip} — {size/1024/1024:.1f}MB")
print(f"\nTotal size: {total_size/1024/1024:.1f}MB")
