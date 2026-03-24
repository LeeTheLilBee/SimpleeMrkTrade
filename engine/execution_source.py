import json
from pathlib import Path


def load_json(path, default):
    try:
        p = Path(path)
        if not p.exists():
            return default
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def get_execution_candidates():
    """
    Returns the exact list of symbols/signals the simulation is allowed to trade.
    Source of truth = data/execution_universe.json

    Also normalizes missing fields so older bot logic can still run.
    """
    universe = load_json("data/execution_universe.json", {})
    if not isinstance(universe, dict):
        return []

    selected = universe.get("selected", [])
    if not isinstance(selected, list):
        return []

    normalized = []
    for item in selected:
        if not isinstance(item, dict):
            continue

        candidate = dict(item)

        # Backfill fields older bot logic expects
        candidate.setdefault("trend", "UPTREND")
        candidate.setdefault("rsi", 55)
        candidate.setdefault("atr", 2.0)
        candidate.setdefault("price", 100.0)
        candidate.setdefault("strategy", "CALL")
        candidate.setdefault("volatility_state", "NORMAL")
        candidate.setdefault("mode", "STANDARD")
        candidate.setdefault("sector", "General")
        candidate.setdefault("current_price", candidate.get("price", 100.0))
        candidate.setdefault("entry", candidate.get("price", 100.0))
        candidate.setdefault("stop", round(candidate.get("price", 100.0) * 0.97, 2))
        candidate.setdefault("target", round(candidate.get("price", 100.0) * 1.10, 2))

        normalized.append(candidate)

    return normalized
