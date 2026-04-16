import json
from pathlib import Path

FILES = {
    "open_positions": "data/open_positions.json",
    "positions": "data/positions.json",
    "account_state": "data/account_state.json",
    "trade_log": "data/trade_log.json",
    "closed_positions": "data/closed_positions.json",
    "candidate_log": "data/candidate_log.json",
    "top_candidates": "data/top_candidates.json",
    "daily_report": "data/daily_report.json",
    "drawdown_history": "data/drawdown_history.json",
    "equity_curve": "data/equity_curve.json",
}

def write_json(path, data):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def main():
    write_json(FILES["open_positions"], [])
    write_json(FILES["positions"], [])
    write_json(FILES["trade_log"], [])
    write_json(FILES["closed_positions"], [])
    write_json(FILES["candidate_log"], [])
    write_json(FILES["top_candidates"], [])
    write_json(FILES["drawdown_history"], [])
    write_json(FILES["equity_curve"], [])
    write_json(FILES["daily_report"], {})

    account_state = {
        "equity": 1000.0,
        "cash": 1000.0,
        "buying_power": 1000.0,
        "account_type": "margin",
        "trade_history": [],
    }
    write_json(FILES["account_state"], account_state)

    print("Runtime/account state reset to clean simulation baseline.")
    print(account_state)

if __name__ == "__main__":
    main()
