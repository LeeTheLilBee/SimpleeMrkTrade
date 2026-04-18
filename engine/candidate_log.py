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
    path = Path(FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data[:MAX_ROWS], f, indent=2)


def clear_candidates() -> None:
    _save([])


def _candidate_key(candidate: Dict[str, Any]) -> str:
    symbol = _safe_str(candidate.get("symbol"), "UNKNOWN").upper()
    strategy = _safe_str(candidate.get("strategy"), "CALL").upper()
    status = _safe_str(candidate.get("status"), "candidate").lower()
    timestamp = _safe_str(candidate.get("timestamp"), "")
    return f"{symbol}|{strategy}|{status}|{timestamp}"


def _normalize_candidate_row(candidate: Dict[str, Any]) -> Dict[str, Any]:
    candidate = _safe_dict(candidate)
    raw = _safe_dict(candidate.get("raw"))
    v2 = _safe_dict(candidate.get("v2"))

    out = dict(candidate)

    out["symbol"] = _safe_str(candidate.get("symbol"), _safe_str(raw.get("symbol"), "UNKNOWN")).upper()
    out["strategy"] = _safe_str(candidate.get("strategy"), _safe_str(raw.get("strategy"), "CALL")).upper()
    out["status"] = _safe_str(candidate.get("status"), "candidate")
    out["timestamp"] = _safe_str(candidate.get("timestamp"), "")
    out["score"] = round(
        _safe_float(
            candidate.get("score", candidate.get("fused_score", raw.get("score", 0.0))),
            0.0,
        ),
        2,
    )
    out["confidence"] = _safe_str(
        candidate.get("confidence", raw.get("confidence", "LOW")),
        "LOW",
    ).upper()
    out["decision_reason"] = _safe_str(
        candidate.get("decision_reason", candidate.get("final_reason", "")),
        "",
    )
    out["decision_label"] = _safe_str(
        candidate.get("decision_label", candidate.get("reason", "")),
        "",
    )
    out["vehicle_selected"] = _safe_str(
        candidate.get("vehicle_selected", raw.get("vehicle_selected", "RESEARCH_ONLY")),
        "RESEARCH_ONLY",
    ).upper()
    out["capital_required"] = round(
        _safe_float(candidate.get("capital_required"), 0.0),
        2,
    )
    out["capital_available"] = round(
        _safe_float(candidate.get("capital_available"), 0.0),
        2,
    )

    out["v2"] = v2
    out["v2_regime_alignment"] = _safe_str(
        candidate.get("v2_regime_alignment", v2.get("regime_alignment", "")),
        "",
    )
    out["v2_signal_strength"] = round(
        _safe_float(candidate.get("v2_signal_strength", v2.get("signal_strength", 0.0)), 0.0),
        2,
    )
    out["v2_conviction_adjustment"] = round(
        _safe_float(candidate.get("v2_conviction_adjustment", v2.get("conviction_adjustment", 0.0)), 0.0),
        2,
    )
    out["v2_vehicle_bias"] = _safe_str(
        candidate.get("v2_vehicle_bias", v2.get("vehicle_bias", "")),
        "",
    ).upper()
    out["v2_thesis"] = _safe_str(
        candidate.get("v2_thesis", v2.get("thesis", "")),
        "",
    )
    out["v2_notes"] = _safe_list(
        candidate.get("v2_notes", v2.get("notes", []))
    )
    out["v2_risk_flags"] = _safe_list(
        candidate.get("v2_risk_flags", v2.get("risk_flags", []))
    )

    return out


def remember_candidate(candidate: Dict[str, Any]) -> None:
    candidate = _normalize_candidate_row(candidate)
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
        vehicle = _safe_str(c.get("vehicle_selected"), "RESEARCH_ONLY")
        capital_required = c.get("capital_required")
        capital_available = c.get("capital_available")
        v2_alignment = _safe_str(c.get("v2_regime_alignment"), "")
        v2_strength = round(_safe_float(c.get("v2_signal_strength"), 0.0), 2)

        capital_text = ""
        if capital_required is not None and capital_available is not None:
            capital_text = (
                f" | capital {round(_safe_float(capital_required), 2)}"
                f" / {round(_safe_float(capital_available), 2)}"
            )

        v2_text = ""
        if v2_alignment or v2_strength != 0:
            v2_text = f" | V2 {v2_alignment or 'n/a'} {v2_strength}"

        print(
            f"{symbol} | {strategy} | {score} | {confidence} | {status} | {vehicle}{capital_text}{v2_text}"
        )
        if reason:
            print(f"  reason: {reason}")
