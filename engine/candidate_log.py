from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

FILE = "data/candidate_log.json"
MAX_ROWS = 400


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _load() -> List[Dict[str, Any]]:
    path = Path(FILE)
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save(data: List[Dict[str, Any]]) -> None:
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data[:MAX_ROWS], f, indent=2)


def clear_candidates() -> None:
    _save([])


def _candidate_key(candidate: Dict[str, Any]) -> str:
    symbol = _safe_str(candidate.get("symbol"), "UNKNOWN").upper()
    strategy = _safe_str(candidate.get("strategy"), "CALL").upper()
    status = _safe_str(candidate.get("status"), "candidate").lower()
    timestamp = _safe_str(candidate.get("timestamp"), "")
    return f"{symbol}|{strategy}|{status}|{timestamp}"


def remember_candidate(candidate: Dict[str, Any]) -> None:
    candidate = _safe_dict(candidate)
    if not candidate:
        return

    data = _load()
    keys = {_candidate_key(row) for row in data if isinstance(row, dict)}
    new_key = _candidate_key(candidate)

    if new_key not in keys:
        data.insert(0, candidate)
    else:
        rebuilt = []
        replaced = False
        for row in data:
            if isinstance(row, dict) and _candidate_key(row) == new_key and not replaced:
                rebuilt.append(candidate)
                replaced = True
            else:
                rebuilt.append(row)
        data = rebuilt

    _save(data)


def get_candidates(limit: int | None = None) -> List[Dict[str, Any]]:
    data = _load()
    if isinstance(limit, int) and limit > 0:
        return data[:limit]
    return data


def show_candidates(limit: int = 25) -> None:
    data = get_candidates(limit=limit)
    print("FUSED CANDIDATE INTELLIGENCE")
    if not data:
        print("None")
        return

    for c in data:
        symbol = _safe_str(c.get("symbol"), "UNKNOWN")
        strategy = _safe_str(c.get("strategy"), "CALL")
        score = round(_safe_float(c.get("score"), 0.0), 2)
        confidence = _safe_str(c.get("confidence"), "LOW")
        status = _safe_str(c.get("status"), "candidate").upper()
        reason = _safe_str(c.get("decision_reason"), c.get("decision_label", ""))
        capital_required = c.get("capital_required")
        capital_available = c.get("capital_available")

        capital_text = ""
        if capital_required is not None and capital_available is not None:
            capital_text = f" | capital {round(_safe_float(capital_required), 2)} / {round(_safe_float(capital_available), 2)}"

        print(
            f"{symbol} | {strategy} | {score} | {confidence} | {status}{capital_text}"
        )
        if reason:
            print(f"  reason: {reason}")
