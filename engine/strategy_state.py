import json

FILE = "data/strategy_state.json"

def save_strategy_state(payload):
    with open(FILE, "w") as f:
        json.dump(payload, f, indent=2)
