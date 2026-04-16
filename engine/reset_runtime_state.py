import json
from pathlib import Path

OPEN_FILE = "data/open_positions.json"
POSITIONS_FILE = "data/positions.json"
ACCOUNT_FILE = "data/account_state.json"

def _write(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def main():
    _write(OPEN_FILE, [])
    _write(POSITIONS_FILE, [])

    if Path(ACCOUNT_FILE).exists():
        with open(ACCOUNT_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
    else:
        state = {}

    state["trade_history"] = []
    _write(ACCOUNT_FILE, state)

    print("Runtime open-position state cleared.")
    print("open_positions.json -> []")
    print("positions.json -> []")
    print("account_state.trade_history -> []")

if __name__ == "__main__":
    main()
