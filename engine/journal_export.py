import csv
import json
from pathlib import Path

TRADE_LOG = "data/trade_log.json"
EXPORT_FILE = "data/trade_journal_export.csv"


def load_json(path, default):
    file_path = Path(path)
    if not file_path.exists():
        return default
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def export_journal():
    trades = load_json(TRADE_LOG, [])
    if not isinstance(trades, list):
        trades = []

    if not trades:
        print("Journal export skipped: no trades found.")
        return

    fieldnames = []
    seen = set()

    for trade in trades:
        if not isinstance(trade, dict):
            continue
        for key in trade.keys():
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)

    Path("data").mkdir(parents=True, exist_ok=True)

    with open(EXPORT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(trades)

    print(f"Journal exported: {EXPORT_FILE}")
