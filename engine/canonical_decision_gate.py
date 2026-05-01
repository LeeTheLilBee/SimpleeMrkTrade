from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional

from engine.canonical_candidate import build_canonical_candidate
from engine.observatory_mode import build_mode_context, normalize_mode


STATE_REJECTED = "rejected"
STATE_RESEARCH_APPROVED_NOT_EXECUTION_READY = "research_approved_not_execution_ready"
STATE_EXECUTION_READY = "execution_ready"
STATE_SELECTED = "selected"
STATE_EXECUTION_READY_NOT_SELECTED = "execution_ready_not_selected"


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


def _safe_bool(value: Any, default: bool = False) -> bool:
    try:
        if value is None:
            return bool(default)
        return bool(value)
    except Exception:
        return bool(default)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "UNKNOWN").upper()


def _dedupe_keep_order(items: List[Any]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in _safe_list(items):
        text = _safe_str(item, "")
        if text and text not in seen:
            seen.add(text)
            out.append(text)
    return out


def _base_output(
    candidate: Dict[str, Any],
    *,
    status: str,
    reason: str,
    reason_code: str,
    blocked_at: str,
    mode: str,
    breadth: str,
    volatility_state: str,
    capital_required: float,
    capital_available: float,
    stronger_competing_setups: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    enriched = deepcopy(_safe_dict(candidate))
    enriched["final_reason"] = reason
    enriched["final_reason_code"] = reason_code
    enriched["decision_reason"] = reason
    enriched["decision_reason_code"] = reason_code
    enriched["blocked_at"] = blocked_at

    research_approved = status in {
        STATE_RESEARCH_APPROVED_NOT_EXECUTION_READY,
        STATE_EXECUTION_READY,
        STATE_SELECTED,
        STATE_EXECUTION_READY_NOT_SELECTED,
    }
    execution_ready = status in {
        STATE_EXECUTION_READY,
        STATE_SELECTED,
        STATE_EXECUTION_READY_NOT_SELECTED,
    }
    selected_for_execution = status == STATE_SELECTED

    enriched["research_approved"] = research_approved
    enriched["execution_ready"] = execution_ready
    enriched["selected_for_execution"] = selected_for_execution

    return build_canonical_candidate(
        enriched,
        status=status,
        reason=reason_code,
        mode=mode,
        breadth=breadth,
        volatility_state=volatility_state,
        decision_reason=reason,
        selected_for_execution=selected_for_execution,
        capital_required=capital_required,
        capital_available=capital_available,
        stronger_competing_setups=stronger_competing_setups or [],
    )


def candidate_rejected(
    candidate: Dict[str, Any],
    *,
    reason: str,
    reason_code: str,
    blocked_at: str,
    mode: str,
    breadth: str,
    volatility_state: str,
    capital_required: float = 0.0,
    capital_available: float = 0.0,
) -> Dict[str, Any]:
    return _base_output(
        candidate,
        status=STATE_REJECTED,
        reason=reason,
        reason_code=reason_code,
        blocked_at=blocked_at,
        mode=mode,
        breadth=breadth,
        volatility_state=volatility_state,
        capital_required=capital_required,
        capital_available=capital_available,
    )


def candidate_research_approved_not_execution_ready(
    candidate: Dict[str, Any],
    *,
    reason: str,
    reason_code: str,
    blocked_at: str,
    mode: str,
    breadth: str,
    volatility_state: str,
    capital_required: float,
    capital_available: float,
) -> Dict[str, Any]:
    return _base_output(
        candidate,
        status=STATE_RESEARCH_APPROVED_NOT_EXECUTION_READY,
        reason=reason,
        reason_code=reason_code,
        blocked_at=blocked_at,
        mode=mode,
        breadth=breadth,
        volatility_state=volatility_state,
        capital_required=capital_required,
        capital_available=capital_available,
    )


def candidate_execution_ready(
    candidate: Dict[str, Any],
    *,
    mode: str,
    breadth: str,
    volatility_state: str,
    capital_required: float,
    capital_available: float,
) -> Dict[str, Any]:
    return _base_output(
        candidate,
        status=STATE_EXECUTION_READY,
        reason="Execution ready.",
        reason_code="execution_ready",
        blocked_at="",
        mode=mode,
        breadth=breadth,
        volatility_state=volatility_state,
        capital_required=capital_required,
        capital_available=capital_available,
    )


def candidate_selected(
    candidate: Dict[str, Any],
    *,
    mode: str,
    breadth: str,
    volatility_state: str,
    capital_required: float,
    capital_available: float,
) -> Dict[str, Any]:
    return _base_output(
        candidate,
        status=STATE_SELECTED,
        reason="Selected for execution.",
        reason_code="selected_for_execution",
        blocked_at="",
        mode=mode,
        breadth=breadth,
        volatility_state=volatility_state,
        capital_required=capital_required,
        capital_available=capital_available,
    )


def candidate_execution_ready_not_selected(
    candidate: Dict[str, Any],
    *,
    stronger_competing_setups: Optional[List[Dict[str, Any]]],
    mode: str,
    breadth: str,
    volatility_state: str,
    capital_required: float,
    capital_available: float,
) -> Dict[str, Any]:
    return _base_output(
        candidate,
        status=STATE_EXECUTION_READY_NOT_SELECTED,
        reason="Approved but ranked below the execution cut.",
        reason_code="approved_but_ranked_below_execution_cut",
        blocked_at="",
        mode=mode,
        breadth=breadth,
        volatility_state=volatility_state,
        capital_required=capital_required,
        capital_available=capital_available,
        stronger_competing_setups=stronger_competing_setups or [],
    )


def stronger_competing_setups(
    candidate: Dict[str, Any],
    selected_trades: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    candidate = _safe_dict(candidate)
    current_symbol = _norm_symbol(candidate.get("symbol"))
    current_strategy = _safe_str(candidate.get("strategy"), "CALL").upper()
    current_score = _safe_float(candidate.get("fused_score", candidate.get("score", 0.0)), 0.0)

    stronger = []
    for other in _safe_list(selected_trades):
        other = _safe_dict(other)
        other_symbol = _norm_symbol(other.get("symbol"))
        other_strategy = _safe_str(other.get("strategy"), "CALL").upper()
        other_score = _safe_float(other.get("fused_score", other.get("score", 0.0)), 0.0)

        if other_symbol == current_symbol and other_strategy == current_strategy:
            continue

        if other_score >= current_score:
            stronger.append({
                "symbol": other_symbol,
                "strategy": other_strategy,
                "score": round(other_score, 4),
            })

    stronger.sort(key=lambda x: x["score"], reverse=True)
    return stronger


def gate_candidate_state(
    candidate: Dict[str, Any],
    *,
    chosen_strategy: str,
    breadth_allowed: bool,
    duplicate_open_found: bool,
    reentry_allowed: bool,
    reentry_reason: str,
    score_allowed: bool,
    volatility_allowed: bool,
    execution_guard_blocked: bool,
    execution_guard_reason: str,
    governor_blocked: bool = False,
    governor_reason: str = "",
    capital_required: float = 0.0,
    capital_available: float = 0.0,
    mode: str = "paper",
    breadth: str = "",
    volatility_state: str = "",
) -> Dict[str, Any]:
    candidate = deepcopy(_safe_dict(candidate))
    mode = normalize_mode(mode)

    if not breadth_allowed:
        return candidate_rejected(
            candidate,
            reason="Breadth filter blocked this setup.",
            reason_code="failed_breadth_filter",
            blocked_at="breadth_guard",
            mode=mode,
            breadth=breadth,
            volatility_state=volatility_state,
            capital_required=capital_required,
            capital_available=capital_available,
        )

    if _safe_str(chosen_strategy, "").upper() == "NO_TRADE":
        return candidate_rejected(
            candidate,
            reason="Strategy router returned no trade.",
            reason_code="strategy_router_returned_no_trade",
            blocked_at="strategy_router",
            mode=mode,
            breadth=breadth,
            volatility_state=volatility_state,
            capital_required=capital_required,
            capital_available=capital_available,
        )

    if duplicate_open_found:
        return candidate_rejected(
            candidate,
            reason="An open position already exists for this setup.",
            reason_code="already_open_position",
            blocked_at="duplicate_guard",
            mode=mode,
            breadth=breadth,
            volatility_state=volatility_state,
            capital_required=capital_required,
            capital_available=capital_available,
        )

    if not reentry_allowed:
        clean_reason = _safe_str(reentry_reason, "reentry_blocked")
        return candidate_rejected(
            candidate,
            reason=f"Reentry blocked: {clean_reason}.",
            reason_code=f"reentry_blocked:{clean_reason}",
            blocked_at="reentry_guard",
            mode=mode,
            breadth=breadth,
            volatility_state=volatility_state,
            capital_required=capital_required,
            capital_available=capital_available,
        )

    if not score_allowed:
        return candidate_rejected(
            candidate,
            reason="Score threshold not met.",
            reason_code="failed_score_threshold",
            blocked_at="score_threshold",
            mode=mode,
            breadth=breadth,
            volatility_state=volatility_state,
            capital_required=capital_required,
            capital_available=capital_available,
        )

    if not volatility_allowed:
        return candidate_rejected(
            candidate,
            reason="Volatility filter blocked this setup.",
            reason_code="failed_volatility_filter",
            blocked_at="volatility_guard",
            mode=mode,
            breadth=breadth,
            volatility_state=volatility_state,
            capital_required=capital_required,
            capital_available=capital_available,
        )

    if governor_blocked:
        clean_reason = _safe_str(governor_reason, "governor_blocked")
        return candidate_research_approved_not_execution_ready(
            candidate,
            reason=f"Governor blocked execution: {clean_reason}.",
            reason_code=clean_reason,
            blocked_at="execution_guard",
            mode=mode,
            breadth=breadth,
            volatility_state=volatility_state,
            capital_required=capital_required,
            capital_available=capital_available,
        )

    if execution_guard_blocked:
        clean_reason = _safe_str(execution_guard_reason, "execution_guard_blocked")
        return candidate_research_approved_not_execution_ready(
            candidate,
            reason=f"Execution guard blocked this setup: {clean_reason}.",
            reason_code=clean_reason,
            blocked_at="execution_guard",
            mode=mode,
            breadth=breadth,
            volatility_state=volatility_state,
            capital_required=capital_required,
            capital_available=capital_available,
        )

    return candidate_execution_ready(
        candidate,
        mode=mode,
        breadth=breadth,
        volatility_state=volatility_state,
        capital_required=capital_required,
        capital_available=capital_available,
    )


def select_execution_candidates(
    execution_ready_candidates: List[Dict[str, Any]],
    selected_trades: List[Dict[str, Any]],
    *,
    mode: str,
    breadth: str,
    volatility_state: str,
    capital_available: float,
) -> Dict[str, List[Dict[str, Any]]]:
    mode = normalize_mode(mode)
    selected_keys = {
        (
            _norm_symbol(t.get("symbol")),
            _safe_str(t.get("strategy"), "CALL").upper(),
        )
        for t in _safe_list(selected_trades)
        if isinstance(t, dict)
    }

    finalized_research_approved: List[Dict[str, Any]] = []
    finalized_selected: List[Dict[str, Any]] = []

    for candidate in _safe_list(execution_ready_candidates):
        candidate = _safe_dict(candidate)
        key = (
            _norm_symbol(candidate.get("symbol")),
            _safe_str(candidate.get("strategy"), "CALL").upper(),
        )
        capital_required = _safe_float(candidate.get("capital_required"), 0.0)

        if key in selected_keys:
            selected = candidate_selected(
                candidate,
                mode=mode,
                breadth=breadth,
                volatility_state=volatility_state,
                capital_required=capital_required,
                capital_available=capital_available,
            )
            finalized_research_approved.append(selected)
            finalized_selected.append(selected)
        else:
            stronger = stronger_competing_setups(candidate, selected_trades)
            waiting = candidate_execution_ready_not_selected(
                candidate,
                stronger_competing_setups=stronger,
                mode=mode,
                breadth=breadth,
                volatility_state=volatility_state,
                capital_required=capital_required,
                capital_available=capital_available,
            )
            finalized_research_approved.append(waiting)

    return {
        "research_approved": finalized_research_approved,
        "selected": finalized_selected,
    }


__all__ = [
    "STATE_REJECTED",
    "STATE_RESEARCH_APPROVED_NOT_EXECUTION_READY",
    "STATE_EXECUTION_READY",
    "STATE_SELECTED",
    "STATE_EXECUTION_READY_NOT_SELECTED",
    "candidate_rejected",
    "candidate_research_approved_not_execution_ready",
    "candidate_execution_ready",
    "candidate_selected",
    "candidate_execution_ready_not_selected",
    "stronger_competing_setups",
    "gate_candidate_state",
    "select_execution_candidates",
]
