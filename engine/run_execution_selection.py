import os
import sys
import json
from pathlib import Path

# 🔥 Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.engine_selection import build_execution_universe, build_execution_summary


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
    system_state = load_json(
        "data/system_state.json",
        {"regime": "Neutral", "volatility": "Normal"}
    )

    universe = build_execution_universe(signals, system_state)
    summary = build_execution_summary(universe)

    save_json("data/execution_universe.json", universe)
    save_json("data/execution_summary.json", summary)

    print("Execution universe built.")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
