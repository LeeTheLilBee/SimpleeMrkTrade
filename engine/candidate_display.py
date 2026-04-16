from __future__ import annotations

from typing import Any, Dict, List


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
        return float(value)
    except Exception:
        return float(default)


def print_candidate_cards(candidates: List[Dict[str, Any]], title: str = "CANDIDATE INTELLIGENCE") -> None:
    rows = _safe_list(candidates)
    print(title)
    if not rows:
        print("None")
        return

    for row in rows:
        if not isinstance(row, dict):
            continue

        symbol = _safe_str(row.get("symbol"), "UNKNOWN")
        strategy = _safe_str(row.get("strategy"), "CALL").upper()
        score = round(_safe_float(row.get("score"), 0.0), 2)
        confidence = _safe_str(row.get("confidence"), "LOW").upper()
        status = _safe_str(row.get("status"), "candidate").upper()
        mode = _safe_str(row.get("mode"), "")
        breadth = _safe_str(row.get("breadth"), "")
        capital_required = row.get("capital_required")
        capital_available = row.get("capital_available")
        decision_reason = _safe_str(row.get("decision_reason"), row.get("decision_label", ""))
        why_lines = _safe_list(row.get("why"))

        print(
            f"{symbol} | {strategy} | score {score} | conf {confidence} | {status}"
        )
        print(
            f"  mode: {mode or 'N/A'} | breadth: {breadth or 'N/A'}"
        )

        if capital_required is not None and capital_available is not None:
            print(
                f"  capital: needs {round(_safe_float(capital_required), 2)} | available {round(_safe_float(capital_available), 2)}"
            )

        if decision_reason:
            print(f"  reason: {decision_reason}")

        if why_lines:
            first = _safe_str(why_lines[0], "")
            if first:
                print(f"  why: {first}")
