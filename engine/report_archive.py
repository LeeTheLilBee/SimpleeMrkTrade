import json
from pathlib import Path
from datetime import datetime
from engine.performance_tracker import performance_summary
from engine.portfolio_summary import portfolio_summary
from engine.account_snapshot import account_snapshot

FILE = "data/recent_reports.json"

def _load():
    if not Path(FILE).exists():
        return []
    with open(FILE, "r") as f:
        return json.load(f)

def _save(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

def archive_report():
    data = _load()

    entry = {
        "timestamp": datetime.now().isoformat(),
        "performance": performance_summary(),
        "portfolio": portfolio_summary(),
        "snapshot": account_snapshot()
    }

    data.append(entry)
    data = data[-20:]
    _save(data)
    return entry
