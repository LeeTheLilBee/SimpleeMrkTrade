import json
from pathlib import Path

def load_json_file(path, default):
    file = Path(path)
    if not file.exists():
        return default
    with open(file, "r") as f:
        return json.load(f)

def get_dashboard_state():
    return {
        "account": load_json_file("data/account_state.json", {}),
        "open_positions": load_json_file("data/open_positions.json", []),
        "closed_positions": load_json_file("data/closed_positions.json", []),
        "trade_log": load_json_file("data/trade_log.json", []),
        "candidate_log": load_json_file("data/candidate_log.json", []),
        "equity_curve": load_json_file("data/equity_curve.json", [1000])
    }
