from typing import Any, Dict, List

from engine_v2.engine_helpers import _save_json, _load_json, now_iso
from engine_v2.behavior_event_log import get_user_behavior_events

PATTERN_FILE = "/content/SimpleeMrkTrade/data_v2/pattern_detection.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _pattern_card(key: str, headline: str, message: str, severity: str = "medium") -> Dict[str, Any]:
    return {
        "key": key,
        "headline": headline,
        "message": message,
        "severity": severity,
    }


def build_pattern_detection(username: str) -> Dict[str, Any]:
    events = get_user_behavior_events(username)

    opened_symbol_count = 0
    changed_mode_count = 0
    symbol_counts: Dict[str, int] = {}

    for event in events:
        row = _safe_dict(event)
        event_type = str(row.get("event_type", "")).strip().lower()
        symbol = str(row.get("symbol", "")).strip().upper()

        if event_type == "opened_symbol":
            opened_symbol_count += 1
            if symbol:
                symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1

        if event_type == "changed_mode":
            changed_mode_count += 1

    patterns: List[Dict[str, Any]] = []

    if opened_symbol_count >= 3:
        patterns.append(_pattern_card(
            "rapid_symbol_rotation",
            "Rapid symbol rotation",
            "You opened several symbols in a short behavior window. That can dilute conviction and clarity.",
            "high" if opened_symbol_count >= 5 else "medium",
        ))

    repeated_symbols = [symbol for symbol, count in symbol_counts.items() if count >= 2]
    for symbol in repeated_symbols[:3]:
        patterns.append(_pattern_card(
            f"repeat_focus_{symbol}",
            f"Repeated focus on {symbol}",
            f"You came back to {symbol} more than once. That may indicate stronger natural interest or unresolved uncertainty.",
            "medium",
        ))

    if changed_mode_count >= 1:
        patterns.append(_pattern_card(
            "mode_shifting",
            "Mode shifting behavior detected",
            "You changed system mode during this learning window. That can be useful, but it may also reflect searching for clarity.",
            "low" if changed_mode_count == 1 else "medium",
        ))

    payload = {
        "username": username,
        "patterns": patterns,
        "meta": {
            "rebuilt_at": now_iso(),
            "pattern_count": len(patterns),
            "opened_symbol_count": opened_symbol_count,
            "changed_mode_count": changed_mode_count,
        },
    }

    _save_json(PATTERN_FILE, payload)
    return payload


def load_pattern_detection() -> Dict[str, Any]:
    payload = _load_json(PATTERN_FILE, {})
    return payload if isinstance(payload, dict) else {}
