from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

MEMORY_FILE = Path("data/research_learning_memory.json")


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def _safe_bool(value: Any, default: bool = False) -> bool:
    try:
        if value is None:
            return bool(default)
        return bool(value)
    except Exception:
        return bool(default)


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "UNKNOWN").upper()


def _now_iso() -> str:
    return datetime.now().isoformat()


def _load_memory() -> Dict[str, Any]:
    try:
        if not MEMORY_FILE.exists():
            return {
                "version": 1,
                "created_at": _now_iso(),
                "updated_at": _now_iso(),
                "symbols": {},
                "events": [],
                "meta": {
                    "mode": "research_learning_only",
                    "execution_influence_allowed": False,
                },
            }

        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data if isinstance(data, dict) else {}
    except Exception:
        return {
            "version": 1,
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
            "symbols": {},
            "events": [],
            "meta": {
                "mode": "research_learning_only",
                "execution_influence_allowed": False,
            },
        }


def _save_memory(memory: Dict[str, Any]) -> Dict[str, Any]:
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    memory["updated_at"] = _now_iso()

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)

    return memory


def _symbol_bucket(memory: Dict[str, Any], symbol: str) -> Dict[str, Any]:
    symbols = memory.setdefault("symbols", {})
    symbol = _norm_symbol(symbol)

    if symbol not in symbols or not isinstance(symbols.get(symbol), dict):
        symbols[symbol] = {
            "symbol": symbol,
            "first_seen": _now_iso(),
            "last_seen": _now_iso(),
            "times_researched": 0,
            "times_research_approved": 0,
            "times_execution_ready": 0,
            "times_selected": 0,
            "times_rejected": 0,
            "times_execution_paused": 0,
            "last_score": 0.0,
            "best_score": 0.0,
            "last_confidence": "UNKNOWN",
            "last_vehicle": "UNKNOWN",
            "last_reason": "",
            "last_blocked_at": "",
            "last_status": "",
            "observed_patterns": [],
            "notes": [],
        }

    return symbols[symbol]


def _trim_events(memory: Dict[str, Any], max_events: int = 750) -> None:
    events = _safe_list(memory.get("events"))
    if len(events) > max_events:
        memory["events"] = events[-max_events:]


def record_research_observation(
    candidate: Dict[str, Any],
    *,
    source: str = "process_signals",
    allow_execution_influence: bool = False,
) -> Dict[str, Any]:
    """
    Stores research observations for later beta review.

    Safety rule:
    - This memory does not change execution by default.
    - It only creates evidence for future tuning.
    """

    candidate = _safe_dict(candidate)
    symbol = _norm_symbol(candidate.get("symbol"))

    memory = _load_memory()
    memory.setdefault("meta", {})
    memory["meta"]["execution_influence_allowed"] = bool(allow_execution_influence)

    bucket = _symbol_bucket(memory, symbol)

    status = _safe_str(candidate.get("status"), "")
    final_reason = _safe_str(
        candidate.get("final_reason", candidate.get("decision_reason", "")),
        "",
    )
    blocked_at = _safe_str(candidate.get("blocked_at"), "")
    vehicle = _safe_str(
        candidate.get("vehicle_selected", candidate.get("vehicle", "UNKNOWN")),
        "UNKNOWN",
    ).upper()
    confidence = _safe_str(candidate.get("confidence"), "UNKNOWN").upper()
    score = round(_safe_float(candidate.get("fused_score", candidate.get("score", 0.0)), 0.0), 4)

    research_approved = _safe_bool(candidate.get("research_approved"), False)
    execution_ready = _safe_bool(candidate.get("execution_ready"), False)
    selected_for_execution = _safe_bool(candidate.get("selected_for_execution"), False)

    bucket["last_seen"] = _now_iso()
    bucket["times_researched"] = int(bucket.get("times_researched", 0)) + 1
    bucket["last_score"] = score
    bucket["best_score"] = max(_safe_float(bucket.get("best_score"), 0.0), score)
    bucket["last_confidence"] = confidence
    bucket["last_vehicle"] = vehicle
    bucket["last_reason"] = final_reason
    bucket["last_blocked_at"] = blocked_at
    bucket["last_status"] = status

    if research_approved:
        bucket["times_research_approved"] = int(bucket.get("times_research_approved", 0)) + 1
    if execution_ready:
        bucket["times_execution_ready"] = int(bucket.get("times_execution_ready", 0)) + 1
    if selected_for_execution:
        bucket["times_selected"] = int(bucket.get("times_selected", 0)) + 1
    if blocked_at:
        bucket["times_rejected"] = int(bucket.get("times_rejected", 0)) + 1
    if "governor_blocked" in final_reason or "execution_paused" in final_reason or blocked_at == "execution_guard":
        bucket["times_execution_paused"] = int(bucket.get("times_execution_paused", 0)) + 1

    pattern_lines: List[str] = []

    if score >= 200:
        pattern_lines.append("Repeated high-score research candidate.")
    if vehicle == "OPTION":
        pattern_lines.append("Options-first candidate observed.")
    if vehicle == "STOCK":
        pattern_lines.append("Stock fallback candidate observed.")
    if blocked_at == "duplicate_guard":
        pattern_lines.append("Duplicate open-position protection triggered.")
    if blocked_at == "execution_guard":
        pattern_lines.append("Research passed but execution guard paused action.")
    if "max_open_positions" in final_reason:
        pattern_lines.append("Portfolio capacity blocked execution.")
    if "daily_entry_cap" in final_reason:
        pattern_lines.append("Daily entry limit blocked execution.")
    if "fresh_catalyst" in final_reason:
        pattern_lines.append("Fresh catalyst requirement affected decision.")

    existing_patterns = bucket.get("observed_patterns", [])
    if not isinstance(existing_patterns, list):
        existing_patterns = []

    for line in pattern_lines:
        if line not in existing_patterns:
            existing_patterns.append(line)

    bucket["observed_patterns"] = existing_patterns[-25:]

    event = {
        "timestamp": _now_iso(),
        "source": source,
        "symbol": symbol,
        "status": status,
        "score": score,
        "confidence": confidence,
        "vehicle": vehicle,
        "research_approved": research_approved,
        "execution_ready": execution_ready,
        "selected_for_execution": selected_for_execution,
        "blocked_at": blocked_at,
        "final_reason": final_reason,
        "execution_influence_allowed": bool(allow_execution_influence),
    }

    memory.setdefault("events", []).append(event)
    _trim_events(memory)
    _save_memory(memory)

    return {
        "saved": True,
        "symbol": symbol,
        "event": event,
        "execution_influence_allowed": bool(allow_execution_influence),
    }


def summarize_research_learning(limit: int = 15) -> Dict[str, Any]:
    memory = _load_memory()
    symbols = _safe_dict(memory.get("symbols"))

    rows: List[Dict[str, Any]] = []

    for symbol, bucket in symbols.items():
        bucket = _safe_dict(bucket)
        rows.append({
            "symbol": symbol,
            "times_researched": int(bucket.get("times_researched", 0)),
            "times_research_approved": int(bucket.get("times_research_approved", 0)),
            "times_execution_ready": int(bucket.get("times_execution_ready", 0)),
            "times_selected": int(bucket.get("times_selected", 0)),
            "times_rejected": int(bucket.get("times_rejected", 0)),
            "times_execution_paused": int(bucket.get("times_execution_paused", 0)),
            "best_score": _safe_float(bucket.get("best_score"), 0.0),
            "last_score": _safe_float(bucket.get("last_score"), 0.0),
            "last_confidence": _safe_str(bucket.get("last_confidence"), "UNKNOWN"),
            "last_vehicle": _safe_str(bucket.get("last_vehicle"), "UNKNOWN"),
            "last_reason": _safe_str(bucket.get("last_reason"), ""),
            "last_blocked_at": _safe_str(bucket.get("last_blocked_at"), ""),
            "observed_patterns": _safe_list(bucket.get("observed_patterns")),
        })

    rows.sort(
        key=lambda row: (
            row["times_researched"],
            row["best_score"],
            row["times_research_approved"],
        ),
        reverse=True,
    )

    return {
        "updated_at": memory.get("updated_at"),
        "execution_influence_allowed": bool(
            _safe_dict(memory.get("meta")).get("execution_influence_allowed", False)
        ),
        "top_symbols": rows[:max(1, int(limit or 15))],
        "event_count": len(_safe_list(memory.get("events"))),
    }


def print_research_learning_summary(limit: int = 15) -> Dict[str, Any]:
    summary = summarize_research_learning(limit=limit)

    print("RESEARCH LEARNING MEMORY")
    print("Execution influence allowed:", summary.get("execution_influence_allowed", False))
    print("Events stored:", summary.get("event_count", 0))

    rows = summary.get("top_symbols", [])
    if not rows:
        print("No research memory yet.")
        return summary

    for row in rows:
        print(
            row.get("symbol", "UNKNOWN"),
            "| researched:",
            row.get("times_researched", 0),
            "| approved:",
            row.get("times_research_approved", 0),
            "| paused:",
            row.get("times_execution_paused", 0),
            "| best:",
            row.get("best_score", 0),
            "| vehicle:",
            row.get("last_vehicle", "UNKNOWN"),
            "| reason:",
            row.get("last_reason", ""),
        )

    return summary


__all__ = [
    "record_research_observation",
    "summarize_research_learning",
    "print_research_learning_summary",
]
