import json
from pathlib import Path

FILE = "data/candidate_log.json"

def _load():
    if not Path(FILE).exists():
        return []
    with open(FILE, "r") as f:
        return json.load(f)

def _save(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

def clear_candidates():
    _save([])

def remember_candidate(candidate):
    data = _load()

    exists = any(
        c.get("symbol") == candidate.get("symbol") and
        c.get("strategy") == candidate.get("strategy")
        for c in data
    )

    if not exists:
        data.append(candidate)
        _save(data)

def show_candidates():
    data = _load()
    print("STOCK-ONLY CANDIDATES")
    if not data:
        print("None")
        return
    for c in data:
        print(c["symbol"], "|", c["strategy"], "|", c["score"], "|", c["confidence"])
