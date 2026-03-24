import json
from pathlib import Path

FILE = "data/premium_feed.json"

def write_premium_feed_item(item):
    path = Path(FILE)

    if not path.exists():
        data = []
    else:
        with open(path, "r") as f:
            data = json.load(f)

    data.append(item)

    # keep last 50 items only
    data = data[-50:]

    with open(path, "w") as f:
        json.dump(data, f, indent=2)
