import json
from datetime import datetime
from engine.performance_tracker import performance_summary
from engine.portfolio_summary import portfolio_summary
from engine.trade_analytics import analytics

FILE = "data/daily_report.json"

def write_daily_report():
    report = {
        "timestamp": datetime.now().isoformat(),
        "performance": performance_summary(),
        "portfolio": portfolio_summary(),
        "analytics": analytics()
    }

    with open(FILE, "w") as f:
        json.dump(report, f, indent=2)

    return report
