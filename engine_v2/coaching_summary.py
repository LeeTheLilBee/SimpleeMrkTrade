from typing import Any, Dict, List

from engine_v2.engine_helpers import _save_json, _load_json, now_iso
from engine_v2.behavior_event_log import build_behavior_event_log_summary

COACHING_FILE = "/content/SimpleeMrkTrade/data_v2/coaching_summary.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _build_insights(summary: Dict[str, Any]) -> List[Dict[str, Any]]:
    summary = _safe_dict(summary)
    counts = _safe_dict(summary.get("counts", {}))
    top_symbols = summary.get("top_symbols", [])

    insights = []

    opened = counts.get("opened_symbol", 0)
    if opened >= 3:
        insights.append({
            "type": "high_activity",
            "headline": "You’ve been moving quickly",
            "message": "You’ve opened several symbols in a short span. Consider slowing down to focus on your strongest ideas.",
        })

    if len(top_symbols) > 0:
        top = top_symbols[0]
        insights.append({
            "type": "symbol_focus",
            "headline": f"You keep returning to {top.get('symbol')}",
            "message": "This may be a signal worth deeper focus instead of jumping between symbols.",
        })

    if counts.get("changed_mode", 0) > 0:
        insights.append({
            "type": "mode_shift",
            "headline": "You changed your experience mode",
            "message": "Your system state is adapting — keep an eye on whether it improves clarity.",
        })

    return insights


def build_coaching_summary(username: str) -> Dict[str, Any]:
    summary = build_behavior_event_log_summary(username)
    insights = _build_insights(summary)

    payload = {
        "username": username,
        "insights": insights,
        "event_summary": summary,
        "meta": {
            "rebuilt_at": now_iso(),
            "insight_count": len(insights),
        },
    }

    _save_json(COACHING_FILE, payload)
    return payload


def load_coaching_summary() -> Dict[str, Any]:
    payload = _load_json(COACHING_FILE, {})
    return payload if isinstance(payload, dict) else {}
