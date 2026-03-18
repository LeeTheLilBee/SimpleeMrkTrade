import json

FILE = "data/volatility_state.json"

def save_volatility_state(payload):
    with open(FILE, "w") as f:
        json.dump(payload, f, indent=2)
