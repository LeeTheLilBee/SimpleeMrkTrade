from typing import Any, Dict, List

from engine_v2.engine_helpers import _save_json, _load_json, now_iso
from engine_v2.coaching_summary import build_coaching_summary
from engine_v2.pattern_detection import build_pattern_detection

LESSON_FEED_FILE = "/content/SimpleeMrkTrade/data_v2/lesson_feed.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _lesson_card(key: str, headline: str, lesson: str, action: str, severity: str = "medium") -> Dict[str, Any]:
    return {
        "key": key,
        "headline": headline,
        "lesson": lesson,
        "action": action,
        "severity": severity,
    }


def build_lesson_feed(username: str) -> Dict[str, Any]:
    coaching = build_coaching_summary(username)
    patterns = build_pattern_detection(username)

    lessons: List[Dict[str, Any]] = []

    for item in _safe_list(coaching.get("insights", [])):
        row = _safe_dict(item)
        kind = str(row.get("type", "")).strip().lower()

        if kind == "high_activity":
            lessons.append(_lesson_card(
                "slow_down",
                "Slow the scan",
                "High activity can reduce clarity when too many symbols compete for attention.",
                "Try staying with the top one or two names before opening more.",
                "medium",
            ))

        elif kind == "symbol_focus":
            lessons.append(_lesson_card(
                "follow_conviction",
                "Follow repeated attention",
                "When you naturally return to the same symbol, it may deserve deeper structured review.",
                "Open the symbol deep dive instead of restarting a broad scan.",
                "medium",
            ))

        elif kind == "mode_shift":
            lessons.append(_lesson_card(
                "use_mode_changes_intentionally",
                "Use mode changes intentionally",
                "Changing modes can help, but it works best when you know why you are switching.",
                "Pause and name what problem the new mode is solving before switching again.",
                "low",
            ))

    for item in _safe_list(patterns.get("patterns", [])):
        row = _safe_dict(item)
        key = str(row.get("key", "")).strip().lower()

        if key == "rapid_symbol_rotation":
            lessons.append(_lesson_card(
                "rotation_pattern",
                "Rotation is becoming a pattern",
                "Repeated fast symbol switching may be turning exploration into noise.",
                "Use Focus Mode and commit to a shorter active list.",
                row.get("severity", "medium"),
            ))

        elif key.startswith("repeat_focus_"):
            symbol = key.replace("repeat_focus_", "").upper()
            lessons.append(_lesson_card(
                f"repeat_focus_{symbol}",
                f"{symbol} may deserve a deeper review",
                f"You are coming back to {symbol}, which may signal stronger conviction than your broader scanning behavior.",
                f"Open {symbol} in the symbol deep dive and compare both lanes carefully.",
                row.get("severity", "medium"),
            ))

        elif key == "mode_shifting":
            lessons.append(_lesson_card(
                "mode_shift_pattern",
                "Mode shifting is showing up in your pattern log",
                "Repeated environment changes can either sharpen clarity or fragment it.",
                "Set a default mode for the session before scanning further.",
                row.get("severity", "low"),
            ))

    payload = {
        "username": username,
        "lessons": lessons[:12],
        "meta": {
            "rebuilt_at": now_iso(),
            "lesson_count": len(lessons[:12]),
        },
    }

    _save_json(LESSON_FEED_FILE, payload)
    return payload


def load_lesson_feed() -> Dict[str, Any]:
    payload = _load_json(LESSON_FEED_FILE, {})
    return payload if isinstance(payload, dict) else {}
