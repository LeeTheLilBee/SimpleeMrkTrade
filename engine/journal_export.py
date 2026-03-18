import json
import csv
from pathlib import Path

def export_journal():
    source = Path("data/trade_log.json")
    target = Path("data/trade_journal_export.csv")

    if not source.exists():
        print("No trade log to export.")
        return

    with open(source, "r") as f:
        trades = json.load(f)

    if not trades:
        print("Trade log empty.")
        return

    keys = list(trades[0].keys())

    with open(target, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(trades)

    print("Journal exported:", target)
