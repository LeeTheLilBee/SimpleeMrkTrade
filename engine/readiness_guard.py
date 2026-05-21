# ==============================================================================
# OBSERVATORY READINESS GUARD
# ==============================================================================
# Canonical readiness + anti-repeat helper for The Observatory.
#
# This file answers:
# - Is this candidate truly ready?
# - Is it only watch-worthy?
# - Is it blocked because the symbol is already open?
# - Is it blocked because recent history says "do not chase this again yet"?
# - What exact reason should the UI / logs / engine show?
#
# Design rules:
# - Compatibility-preserving.
# - No hard dependency on one candidate shape.
# - Safe for paper/live/survey style modes.
# - Does not execute trades.
# - Does not mutate active books.
# ==============================================================================

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple


READY = "READY"
WATCH = "WATCH"
WEAK = "WEAK"
BLOCKED = "BLOCKED"
DUPLICATE = "DUPLICATE"
NO_TRADE = "NO_TRADE"


DEFAULTS = {
    "min_ready_score": 100.0,
    "min_watch_score": 75.0,
    "min_ready_contract_score": 70.0,
    "min_watch_contract_score": 55.0,
    "recent_trade_cooldown_hours": 24,
    "require_strategy_confirmed": True,
    "allow_stock_fallback": True,
    "live_requires_executable_option": True,
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_upper(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    if not text:
        return default
    return text.upper()


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        if isinstance(value, str) and not value.strip():
            return default
        return float(value)
    except Exception:
        return default


def _safe_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "allowed", "ok", "pass"}:
        return True
    if text in {"0", "false", "no", "n", "blocked", "fail"}:
        return False
    return default


def _trade_id(row: Dict[str, Any]) -> str:
    return str(row.get("trade_id") or row.get("id") or row.get("order_id") or "").strip()


def _symbol(row: Dict[str, Any]) -> str:
    return _safe_upper(row.get("symbol") or row.get("ticker") or "")


def _strategy(row: Dict[str, Any]) -> str:
    return _safe_upper(
        row.get("final_strategy")
        or row.get("chosen_strategy")
        or row.get("strategy")
        or row.get("starting_strategy")
        or row.get("direction")
        or ""
    )


def _starting_strategy(row: Dict[str, Any]) -> str:
    return _safe_upper(row.get("starting_strategy") or row.get("strategy") or "")


def _vehicle(row: Dict[str, Any]) -> str:
    return _safe_upper(
        row.get("vehicle_selected")
        or row.get("selected_vehicle")
        or row.get("vehicle")
        or row.get("asset_type")
        or ""
    )


def _confidence(row: Dict[str, Any]) -> str:
    return _safe_upper(row.get("confidence") or row.get("base_confidence") or "")


def _is_open_position_match(candidate: Dict[str, Any], position: Dict[str, Any]) -> bool:
    cand_symbol = _symbol(candidate)
    pos_symbol = _symbol(position)

    if not cand_symbol or not pos_symbol:
        return False

    if cand_symbol != pos_symbol:
        return False

    cand_strategy = _strategy(candidate)
    pos_strategy = _strategy(position)

    if cand_strategy and pos_strategy and cand_strategy != pos_strategy:
        return False

    return True


def _is_recent_closed_match(candidate: Dict[str, Any], closed: Dict[str, Any]) -> bool:
    cand_symbol = _symbol(candidate)
    closed_symbol = _symbol(closed)

    if not cand_symbol or not closed_symbol:
        return False

    if cand_symbol != closed_symbol:
        return False

    cand_strategy = _strategy(candidate)
    closed_strategy = _strategy(closed)

    if cand_strategy and closed_strategy and cand_strategy != closed_strategy:
        return False

    return True


def find_duplicate_open_position(
    candidate: Dict[str, Any],
    open_positions: Optional[Iterable[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    rows = list(open_positions or [])

    for row in rows:
        if not isinstance(row, dict):
            continue

        if _is_open_position_match(candidate, row):
            return {
                "duplicate_open_found": True,
                "duplicate_trade_id": _trade_id(row),
                "duplicate_symbol": _symbol(row),
                "duplicate_strategy": _strategy(row),
                "duplicate_vehicle": _vehicle(row),
                "reason": "already_open_position",
                "detail": "Research saw the setup, but the symbol is already open in the active book.",
            }

    return {
        "duplicate_open_found": False,
        "duplicate_trade_id": "",
        "duplicate_symbol": "",
        "duplicate_strategy": "",
        "duplicate_vehicle": "",
        "reason": "",
        "detail": "",
    }


def evaluate_reentry(
    candidate: Dict[str, Any],
    closed_positions: Optional[Iterable[Dict[str, Any]]] = None,
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    cfg = dict(DEFAULTS)
    if isinstance(config, dict):
        cfg.update(config)

    rows = list(closed_positions or [])
    candidate_score = _safe_float(candidate.get("score") or candidate.get("base_score"), 0.0)
    candidate_confidence = _confidence(candidate)

    recent_matches: List[Dict[str, Any]] = []

    for row in rows:
        if not isinstance(row, dict):
            continue

        if _is_recent_closed_match(candidate, row):
            recent_matches.append(row)

    if not recent_matches:
        return {
            "reentry_allowed": True,
            "reentry_reason": "no_recent_closed_trade",
            "recent_match_count": 0,
            "recent_trade_id": "",
            "score_improved": True,
            "confidence_improved": True,
        }

    latest = recent_matches[-1]
    latest_score = _safe_float(latest.get("score") or latest.get("base_score"), 0.0)
    latest_confidence = _safe_upper(latest.get("confidence") or "")

    score_improved = candidate_score > latest_score
    confidence_rank = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CONTROLLED": 4}
    confidence_improved = confidence_rank.get(candidate_confidence, 0) >= confidence_rank.get(latest_confidence, 0)

    latest_pnl = _safe_float(latest.get("pnl") or latest.get("realized_pnl"), 0.0)
    latest_reason = _safe_upper(latest.get("close_reason") or latest.get("reason") or "")

    if latest.get("exclude_from_performance") is True or latest.get("controlled_test") is True:
        return {
            "reentry_allowed": True,
            "reentry_reason": "recent_close_not_guarded",
            "recent_match_count": len(recent_matches),
            "recent_trade_id": _trade_id(latest),
            "score_improved": score_improved,
            "confidence_improved": confidence_improved,
        }

    if latest_pnl < 0 and not score_improved:
        return {
            "reentry_allowed": False,
            "reentry_reason": "recent_loss_score_not_improved",
            "recent_match_count": len(recent_matches),
            "recent_trade_id": _trade_id(latest),
            "score_improved": score_improved,
            "confidence_improved": confidence_improved,
        }

    if "STOP" in latest_reason and not score_improved:
        return {
            "reentry_allowed": False,
            "reentry_reason": "recent_stop_score_not_improved",
            "recent_match_count": len(recent_matches),
            "recent_trade_id": _trade_id(latest),
            "score_improved": score_improved,
            "confidence_improved": confidence_improved,
        }

    if not score_improved and not confidence_improved:
        return {
            "reentry_allowed": False,
            "reentry_reason": "score_not_improved_enough,confidence_not_improved",
            "recent_match_count": len(recent_matches),
            "recent_trade_id": _trade_id(latest),
            "score_improved": score_improved,
            "confidence_improved": confidence_improved,
        }

    return {
        "reentry_allowed": True,
        "reentry_reason": "reentry_allowed_with_caution",
        "recent_match_count": len(recent_matches),
        "recent_trade_id": _trade_id(latest),
        "score_improved": score_improved,
        "confidence_improved": confidence_improved,
    }


def _strategy_confirmed(candidate: Dict[str, Any]) -> bool:
    final_strategy = _strategy(candidate)
    starting = _starting_strategy(candidate)

    if final_strategy in {"", NO_TRADE, "NONE", "NO"}:
        return False

    if starting and final_strategy and starting != final_strategy:
        if final_strategy == NO_TRADE:
            return False

    return True


def _option_allowed(candidate: Dict[str, Any]) -> Tuple[bool, str]:
    vehicle = _vehicle(candidate)

    if vehicle != "OPTION":
        return True, "not_option"

    explicit_allowed = candidate.get("option_allowed")
    if explicit_allowed is not None:
        allowed = _safe_bool(explicit_allowed, False)
        reason = str(candidate.get("option_reason") or candidate.get("execution_reason") or "")
        return allowed, reason or ("ok" if allowed else "option_not_allowed")

    option_obj = candidate.get("option") if isinstance(candidate.get("option"), dict) else {}
    contract_obj = candidate.get("contract") if isinstance(candidate.get("contract"), dict) else {}

    execution_category = _safe_upper(
        candidate.get("execution_category")
        or option_obj.get("execution_category")
        or contract_obj.get("execution_category")
        or ""
    )

    if execution_category == "OBSERVED_ONLY":
        return False, str(candidate.get("execution_reason") or "option_observed_only")

    is_executable = candidate.get("is_executable")
    if is_executable is None:
        is_executable = option_obj.get("is_executable", contract_obj.get("is_executable", None))

    if is_executable is not None and not _safe_bool(is_executable, False):
        return False, str(candidate.get("execution_reason") or option_obj.get("execution_reason") or "option_not_executable")

    return True, str(candidate.get("option_reason") or candidate.get("execution_reason") or "ok")


def _capital_allowed(candidate: Dict[str, Any]) -> Tuple[bool, str]:
    capital_required = _safe_float(candidate.get("capital_required") or candidate.get("minimum_trade_cost"), 0.0)
    capital_available = _safe_float(candidate.get("capital_available") or candidate.get("buying_power") or candidate.get("cash"), 0.0)

    if capital_required <= 0:
        return False, "missing_or_zero_capital_required"

    if capital_available > 0 and capital_required > capital_available:
        return False, "insufficient_capital"

    return True, "capital_ok"


def evaluate_readiness(
    candidate: Dict[str, Any],
    open_positions: Optional[Iterable[Dict[str, Any]]] = None,
    closed_positions: Optional[Iterable[Dict[str, Any]]] = None,
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    cfg = dict(DEFAULTS)
    if isinstance(config, dict):
        cfg.update(config)

    c = deepcopy(candidate if isinstance(candidate, dict) else {})

    symbol = _symbol(c)
    score = _safe_float(c.get("score") or c.get("base_score"), 0.0)
    contract_score = _safe_float(
        c.get("option_contract_score")
        or c.get("contract_score")
        or c.get("selected_contract_score"),
        0.0,
    )
    confidence = _confidence(c)
    vehicle = _vehicle(c)
    final_strategy = _strategy(c)

    reasons: List[str] = []
    details: List[str] = []
    blockers: List[str] = []
    warnings: List[str] = []

    duplicate = find_duplicate_open_position(c, open_positions)
    if duplicate["duplicate_open_found"]:
        return {
            **c,
            "symbol": symbol,
            "readiness_status": DUPLICATE,
            "research_approved": False,
            "execution_ready": False,
            "selected_for_execution": False,
            "blocked_at": "duplicate_guard",
            "final_reason": "already_open_position",
            "final_reason_detail": duplicate["detail"],
            "duplicate_open_found": True,
            "duplicate_trade_id": duplicate["duplicate_trade_id"],
            "readiness_score": score,
            "readiness_reasons": ["already_open_position"],
            "readiness_blockers": ["already_open_position"],
            "readiness_warnings": [],
            "readiness_checked_at": _now_iso(),
        }

    reentry = evaluate_reentry(c, closed_positions, cfg)
    if not reentry["reentry_allowed"]:
        return {
            **c,
            "symbol": symbol,
            "readiness_status": BLOCKED,
            "research_approved": False,
            "execution_ready": False,
            "selected_for_execution": False,
            "blocked_at": "reentry_guard",
            "final_reason": f"reentry_blocked:{reentry['reentry_reason']}",
            "final_reason_detail": "Re-entry guard blocked this setup based on recent trade history.",
            "duplicate_open_found": False,
            "duplicate_trade_id": "",
            **reentry,
            "readiness_score": score,
            "readiness_reasons": [reentry["reentry_reason"]],
            "readiness_blockers": [reentry["reentry_reason"]],
            "readiness_warnings": [],
            "readiness_checked_at": _now_iso(),
        }

    if cfg.get("require_strategy_confirmed", True) and not _strategy_confirmed(c):
        return {
            **c,
            "symbol": symbol,
            "readiness_status": NO_TRADE,
            "research_approved": False,
            "execution_ready": False,
            "selected_for_execution": False,
            "blocked_at": "strategy_router",
            "final_reason": "strategy_router_returned_no_trade",
            "final_reason_detail": "Strategy router did not confirm the starting thesis.",
            "duplicate_open_found": False,
            "duplicate_trade_id": "",
            **reentry,
            "readiness_score": score,
            "readiness_reasons": ["strategy_router_returned_no_trade"],
            "readiness_blockers": ["strategy_router_returned_no_trade"],
            "readiness_warnings": [],
            "readiness_checked_at": _now_iso(),
        }

    option_ok, option_reason = _option_allowed(c)
    capital_ok, capital_reason = _capital_allowed(c)

    if score >= cfg["min_ready_score"]:
        reasons.append("score_ready")
    elif score >= cfg["min_watch_score"]:
        warnings.append("score_watch_only")
    else:
        blockers.append("failed_score_threshold")

    if vehicle == "OPTION":
        if option_ok:
            reasons.append("option_contract_allowed")
        else:
            blockers.append(option_reason or "option_not_allowed")

        if contract_score >= cfg["min_ready_contract_score"]:
            reasons.append("contract_score_ready")
        elif contract_score >= cfg["min_watch_contract_score"]:
            warnings.append("contract_score_watch_only")
        else:
            if contract_score > 0:
                blockers.append("contract_score_too_low")

    if capital_ok:
        reasons.append("capital_ok")
    else:
        blockers.append(capital_reason)

    governor_blocked = _safe_bool(c.get("governor_blocked"), False)
    governor_reason = str(c.get("governor_reason") or c.get("execution_guard_reason") or "")

    if governor_blocked:
        blockers.append(governor_reason or "governor_blocked")

    if blockers:
        status = BLOCKED
        research_approved = False
        execution_ready = False

        if score >= cfg["min_ready_score"] and "governor_blocked" in ",".join(blockers):
            research_approved = True

        final_reason = blockers[0]
        detail = _plain_detail(final_reason)

    elif warnings:
        status = WATCH
        research_approved = True
        execution_ready = False
        final_reason = warnings[0]
        detail = _plain_detail(final_reason)

    else:
        status = READY
        research_approved = True
        execution_ready = True
        final_reason = "ready_for_execution"
        detail = "Candidate cleared readiness, duplicate, re-entry, option, and capital checks."

    return {
        **c,
        "symbol": symbol,
        "final_strategy": final_strategy,
        "vehicle_selected": vehicle,
        "readiness_status": status,
        "research_approved": research_approved,
        "execution_ready": execution_ready,
        "selected_for_execution": False,
        "blocked_at": "" if status == READY else ("execution_guard" if governor_blocked else "readiness_guard"),
        "final_reason": final_reason,
        "final_reason_detail": detail,
        "duplicate_open_found": False,
        "duplicate_trade_id": "",
        **reentry,
        "option_allowed": option_ok,
        "option_reason": option_reason,
        "capital_allowed": capital_ok,
        "capital_reason": capital_reason,
        "readiness_score": score,
        "readiness_reasons": reasons,
        "readiness_blockers": blockers,
        "readiness_warnings": warnings,
        "readiness_checked_at": _now_iso(),
    }


def _plain_detail(reason: str) -> str:
    reason = str(reason or "")

    mapping = {
        "failed_score_threshold": "Candidate did not clear the minimum research approval score.",
        "contract_score_too_low": "Option contract quality was not strong enough for execution.",
        "option_not_allowed": "Option path did not clear execution quality checks.",
        "option_observed_only": "Option was useful for research but not safe for execution.",
        "missing_or_zero_capital_required": "Candidate is missing usable capital requirement data.",
        "insufficient_capital": "Candidate costs more than available capital allows.",
        "score_watch_only": "Candidate is worth watching, but not strong enough for execution.",
        "contract_score_watch_only": "Contract is watchable, but not strong enough for execution.",
        "ready_for_execution": "Candidate cleared readiness checks.",
    }

    if reason.startswith("governor_blocked"):
        return "The Observatory can keep researching, but risk rules are pausing execution."

    return mapping.get(reason, reason.replace("_", " ").strip().capitalize() or "Readiness guard reviewed this setup.")


def evaluate_candidates(
    candidates: Iterable[Dict[str, Any]],
    open_positions: Optional[Iterable[Dict[str, Any]]] = None,
    closed_positions: Optional[Iterable[Dict[str, Any]]] = None,
    config: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    for candidate in candidates or []:
        if not isinstance(candidate, dict):
            continue

        results.append(
            evaluate_readiness(
                candidate,
                open_positions=open_positions,
                closed_positions=closed_positions,
                config=config,
            )
        )

    return results


def summarize_readiness(rows: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    items = [r for r in rows or [] if isinstance(r, dict)]

    counts: Dict[str, int] = {}
    blockers: Dict[str, int] = {}

    for row in items:
        status = str(row.get("readiness_status") or "UNKNOWN")
        counts[status] = counts.get(status, 0) + 1

        reason = str(row.get("final_reason") or "")
        if reason:
            blockers[reason] = blockers.get(reason, 0) + 1

    ready = [r for r in items if r.get("readiness_status") == READY]
    watch = [r for r in items if r.get("readiness_status") == WATCH]
    blocked = [r for r in items if r.get("readiness_status") in {BLOCKED, DUPLICATE, NO_TRADE}]

    return {
        "total": len(items),
        "counts": counts,
        "ready_count": len(ready),
        "watch_count": len(watch),
        "blocked_count": len(blocked),
        "ready_symbols": [_symbol(r) for r in ready],
        "watch_symbols": [_symbol(r) for r in watch],
        "top_blockers": sorted(blockers.items(), key=lambda x: x[1], reverse=True)[:10],
        "summary_generated_at": _now_iso(),
    }


def self_test() -> Dict[str, Any]:
    open_positions = [
        {
            "trade_id": "AMD-CALL-OPEN",
            "symbol": "AMD",
            "strategy": "CALL",
            "vehicle": "OPTION",
        }
    ]

    closed_positions = [
        {
            "trade_id": "MSFT-CALL-CLOSED",
            "symbol": "MSFT",
            "strategy": "CALL",
            "score": 100,
            "confidence": "HIGH",
            "pnl": -20,
            "close_reason": "STOP_LOSS",
        }
    ]

    candidates = [
        {
            "symbol": "AMD",
            "starting_strategy": "CALL",
            "final_strategy": "CALL",
            "score": 400,
            "confidence": "HIGH",
            "vehicle_selected": "OPTION",
            "option_contract_score": 120,
            "option_allowed": True,
            "capital_required": 100,
            "capital_available": 1000,
        },
        {
            "symbol": "NVDA",
            "starting_strategy": "CALL",
            "final_strategy": "CALL",
            "score": 220,
            "confidence": "HIGH",
            "vehicle_selected": "OPTION",
            "option_contract_score": 110,
            "option_allowed": True,
            "capital_required": 250,
            "capital_available": 1000,
        },
        {
            "symbol": "MSFT",
            "starting_strategy": "CALL",
            "final_strategy": "CALL",
            "score": 90,
            "confidence": "MEDIUM",
            "vehicle_selected": "STOCK",
            "capital_required": 100,
            "capital_available": 1000,
        },
        {
            "symbol": "UBER",
            "starting_strategy": "PUT",
            "final_strategy": "NO_TRADE",
            "score": 120,
            "confidence": "MEDIUM",
            "vehicle_selected": "OPTION",
            "option_contract_score": 90,
            "option_allowed": True,
            "capital_required": 100,
            "capital_available": 1000,
        },
    ]

    evaluated = evaluate_candidates(
        candidates,
        open_positions=open_positions,
        closed_positions=closed_positions,
    )

    return {
        "evaluated": evaluated,
        "summary": summarize_readiness(evaluated),
        "expected": {
            "AMD": "DUPLICATE",
            "NVDA": "READY",
            "MSFT": "BLOCKED or WATCH depending reentry/score",
            "UBER": "NO_TRADE",
        },
    }


__all__ = [
    "READY",
    "WATCH",
    "WEAK",
    "BLOCKED",
    "DUPLICATE",
    "NO_TRADE",
    "evaluate_readiness",
    "evaluate_candidates",
    "evaluate_reentry",
    "find_duplicate_open_position",
    "summarize_readiness",
    "self_test",
]
