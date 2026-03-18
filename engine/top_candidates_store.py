import json

FILE = "data/top_candidates.json"

def save_top_candidates(trades, limit=10):
    ranked = sorted(trades, key=lambda x: x["score"], reverse=True)[:limit]

    with open(FILE, "w") as f:
        json.dump(ranked, f, indent=2)
