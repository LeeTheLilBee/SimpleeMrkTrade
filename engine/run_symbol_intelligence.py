import os
import sys
import json
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.symbol_intelligence import build_symbol_intelligence


def load_json(path, default):
    try:
        p = Path(path)
        if not p.exists():
            return default
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, payload):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def main():
    signals = load_json("data/signals.json", [])
    execution_universe = load_json("data/execution_universe.json", {})

    symbols = build_symbol_intelligence(signals, execution_universe)
    save_json("data/symbol_intelligence.json", symbols)

    print(f"Built intelligence for {len(symbols)} symbols.")


if __name__ == "__main__":
    main()
