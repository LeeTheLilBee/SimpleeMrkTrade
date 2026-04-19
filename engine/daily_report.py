from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from engine.performance_tracker import performance_summary
from engine.portfolio_summary import portfolio_summary
from engine.trade_analytics import analytics

FILE = "data/daily_report.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _write_json(path_str: str, payload: Any) -> None:
    Path(path_str).parent.mkdir(parents=True, exist_ok=True)
    with open(path_str, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def write_daily_report():
    performance = _safe_dict(performance_summary())
    portfolio = _safe_dict(portfolio_summary())
    analytics_payload = _safe_dict(analytics())

    report = {
        "timestamp": datetime.now().isoformat(),
        "performance": performance,
        "portfolio": portfolio,
        "analytics": analytics_payload,
        "headline": {
            "trades": analytics_payload.get("trades", 0),
            "winrate": analytics_payload.get("winrate", 0.0),
            "realized_pnl": portfolio.get("realized_pnl", 0.0),
            "unrealized_pnl": portfolio.get("unrealized_pnl", 0.0),
            "open_positions": portfolio.get("open_positions", 0),
        },
    }

    _write_json(FILE, report)
    return report
