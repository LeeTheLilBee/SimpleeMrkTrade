# ==============================================================================
# OBSERVATORY RE-ENTRY DISCIPLINE GUARD
# ==============================================================================
# Purpose:
# - Prevent the Observatory from closing a symbol and immediately re-opening
#   the same symbol/setup without a stronger reason.
# - This protects the engine from churn, revenge-reentry, stale repeat trades,
#   and "same idea, new ticket" behavior.
#
# Core rule:
# - A same-symbol recent close enters cooldown.
# - A recent profitable close needs either:
#     1. enough time passed, or
#     2. meaningfully better score/confidence, or
#     3. explicit fresh catalyst/fresh_setup flag.
# - A recent loss is stricter.
# ==============================================================================

from __future__ import annotations

import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
CLOSED_POSITIONS_FILE = DATA_DIR / "closed_positions.json"

DEFAULT_PROFIT_COOLDOWN_HOURS = 24.0
DEFAULT_LOSS_COOLDOWN_HOURS = 48.0
DEFAULT_FLAT_COOLDOWN_HOURS = 18.0

DEFAULT_MIN_SCORE_IMPROVEMENT_PCT = 0.12
DEFAULT_MIN_SCORE_IMPROVEMENT_ABS = 35.0

HIGH_CONFIDENCE_VALUES = {"HIGH", "VERY_HIGH", "ELITE", "A", "A+"}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _safe_upper(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    if not text:
        return default
    return text.upper()


def _safe_float(value: Any, default: Optional[float] = None) -> Optional[float]:
    try:
        if value is None:
            return default
        if isinstance(value, str) and not value.strip():
            return default
        return float(value)
    except Exception:
        return default


def _read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return deepcopy(default)
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return deepcopy(default)


def _as_rows(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]

    if isinstance(data, dict):
        for key in ("closed_positions", "positions", "rows", "data", "trades"):
            value = data.get(key)
            if isinstance(value, list):
                return [row for row in value if isinstance(row, dict)]

    return []


def load_closed_positions() -> List[Dict[str, Any]]:
    return _as_rows(_read_json(CLOSED_POSITIONS_FILE, []))


def _trade_id(row: Dict[str, Any]) -> str:
    return str(row.get("trade_id") or row.get("id") or row.get("order_id") or "").strip()


def _symbol(row: Dict[str, Any]) -> str:
    return _safe_upper(row.get("symbol") or row.get("ticker") or "")


def _strategy(row: Dict[str, Any]) -> str:
    return _safe_upper(
        row.get("strategy")
        or row.get("final_strategy")
        or row.get("starting_strategy")
        or row.get("direction")
        or ""
    )


def _confidence_rank(value: Any) -> int:
    text = _safe_upper(value)
    ranks = {
        "LOW": 1,
        "MEDIUM": 2,
        "MID": 2,
        "HIGH": 3,
        "VERY_HIGH": 4,
        "ELITE": 5,
        "CONTROLLED": 0,
    }
    return ranks.get(text, 0)


def _parse_time(value: Any) -> Optional[datetime]:
    if not value:
        return None

    text = str(value).strip()

    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"

        parsed = datetime.fromisoformat(text)

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return parsed
    except Exception:
        pass

    m = re.search(r"(20\d{12})", text)
    if m:
        try:
            return datetime.strptime(m.group(1), "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
        except Exception:
            return None

    return None


def _row_time(row: Dict[str, Any]) -> Optional[datetime]:
    for key in (
        "closed_at",
        "exited_at",
        "exit_time",
        "timestamp",
        "updated_at",
        "created_at",
        "opened_at",
    ):
        parsed = _parse_time(row.get(key))
        if parsed:
            return parsed

    return _parse_time(_trade_id(row))


def _pnl(row: Dict[str, Any]) -> float:
    return float(
        _safe_float(
            row.get("pnl")
            if row.get("pnl") is not None
            else row.get("realized_pnl")
            if row.get("realized_pnl") is not None
            else row.get("profit_loss"),
            0.0,
        )
        or 0.0
    )


def _score(row: Dict[str, Any]) -> float:
    return float(
        _safe_float(
            row.get("score")
            if row.get("score") is not None
            else row.get("readiness_score")
            if row.get("readiness_score") is not None
            else row.get("base_score")
            if row.get("base_score") is not None
            else row.get("final_score"),
            0.0,
        )
        or 0.0
    )


def _has_fresh_catalyst(candidate: Dict[str, Any]) -> bool:
    truthy_flags = [
        "fresh_catalyst",
        "fresh_setup",
        "new_thesis",
        "thesis_changed",
        "major_catalyst",
        "catalyst_confirmed",
        "fresh_news_confirmed",
        "setup_refresh_confirmed",
    ]

    for key in truthy_flags:
        if bool(candidate.get(key)):
            return True

    reason_text = " ".join(
        str(candidate.get(key, ""))
        for key in (
            "reason",
            "decision_reason",
            "final_reason",
            "final_reason_detail",
            "catalyst",
            "catalyst_summary",
            "thesis",
            "why",
        )
    ).upper()

    fresh_words = (
        "FRESH CATALYST",
        "NEW CATALYST",
        "EARNINGS",
        "GUIDANCE",
        "UPGRADE",
        "DOWNGRADE",
        "BREAKOUT CONFIRMED",
        "NEWS CONFIRMED",
        "THESIS CHANGED",
        "NEW SETUP",
    )

    return any(word in reason_text for word in fresh_words)


def find_recent_symbol_closes(
    candidate: Dict[str, Any],
    closed_positions: Optional[Iterable[Dict[str, Any]]] = None,
    lookback_hours: float = 72.0,
    now: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    now = now or _now()

    symbol = _symbol(candidate)
    strategy = _strategy(candidate)

    if not symbol:
        return []

    rows = list(closed_positions) if closed_positions is not None else load_closed_positions()

    matches: List[Dict[str, Any]] = []

    for row in rows:
        if not isinstance(row, dict):
            continue

        if _symbol(row) != symbol:
            continue

        row_strategy = _strategy(row)
        same_strategy = bool(strategy and row_strategy and strategy == row_strategy)

        closed_at = _row_time(row)
        if not closed_at:
            continue

        hours_since = (now - closed_at).total_seconds() / 3600

        if hours_since < 0:
            # Clock weirdness. Treat as fresh so it does not slip through.
            hours_since = 0.0

        if hours_since <= lookback_hours:
            match = deepcopy(row)
            match["_guard_hours_since_close"] = round(hours_since, 4)
            match["_guard_same_strategy"] = same_strategy
            matches.append(match)

    matches.sort(key=lambda r: r.get("_guard_hours_since_close", 999999))
    return matches


def score_improved_enough(
    candidate: Dict[str, Any],
    previous: Dict[str, Any],
    min_pct: float = DEFAULT_MIN_SCORE_IMPROVEMENT_PCT,
    min_abs: float = DEFAULT_MIN_SCORE_IMPROVEMENT_ABS,
) -> Tuple[bool, Dict[str, Any]]:
    new_score = _score(candidate)
    old_score = _score(previous)

    abs_improvement = new_score - old_score

    if old_score > 0:
        pct_improvement = abs_improvement / old_score
    else:
        pct_improvement = 1.0 if new_score > 0 else 0.0

    improved = abs_improvement >= min_abs or pct_improvement >= min_pct

    return improved, {
        "new_score": new_score,
        "previous_score": old_score,
        "score_abs_improvement": round(abs_improvement, 4),
        "score_pct_improvement": round(pct_improvement, 4),
        "min_score_improvement_abs": min_abs,
        "min_score_improvement_pct": min_pct,
    }


def confidence_improved(candidate: Dict[str, Any], previous: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    new_conf = candidate.get("confidence") or candidate.get("base_confidence")
    old_conf = previous.get("confidence") or previous.get("base_confidence")

    new_rank = _confidence_rank(new_conf)
    old_rank = _confidence_rank(old_conf)

    return new_rank > old_rank, {
        "new_confidence": new_conf,
        "previous_confidence": old_conf,
        "new_confidence_rank": new_rank,
        "previous_confidence_rank": old_rank,
    }


def evaluate_reentry_discipline(
    candidate: Dict[str, Any],
    closed_positions: Optional[Iterable[Dict[str, Any]]] = None,
    now: Optional[datetime] = None,
    profit_cooldown_hours: float = DEFAULT_PROFIT_COOLDOWN_HOURS,
    loss_cooldown_hours: float = DEFAULT_LOSS_COOLDOWN_HOURS,
    flat_cooldown_hours: float = DEFAULT_FLAT_COOLDOWN_HOURS,
    lookback_hours: float = 72.0,
) -> Dict[str, Any]:
    now = now or _now()
    candidate = deepcopy(candidate) if isinstance(candidate, dict) else {}

    symbol = _symbol(candidate)

    result: Dict[str, Any] = {
        "symbol": symbol,
        "allowed": True,
        "status": "CLEAR",
        "reason": "no_recent_closed_trade",
        "reason_detail": "No recent same-symbol close was found inside the re-entry lookback window.",
        "blocked": False,
        "warning": False,
        "recent_match_count": 0,
        "recent_trade_id": "",
        "hours_since_close": None,
        "cooldown_hours_required": 0.0,
        "fresh_catalyst": _has_fresh_catalyst(candidate),
        "score_improved": False,
        "confidence_improved": False,
        "same_strategy": False,
        "guard_checked_at": now.isoformat(),
    }

    if not symbol:
        result.update({
            "allowed": False,
            "status": "BLOCKED",
            "reason": "missing_symbol",
            "reason_detail": "Candidate has no symbol, so re-entry discipline cannot safely evaluate it.",
            "blocked": True,
        })
        return result

    matches = find_recent_symbol_closes(
        candidate,
        closed_positions=closed_positions,
        lookback_hours=lookback_hours,
        now=now,
    )

    result["recent_match_count"] = len(matches)

    if not matches:
        return result

    recent = matches[0]
    pnl = _pnl(recent)
    hours_since = float(recent.get("_guard_hours_since_close") or 0.0)

    if pnl > 0:
        cooldown_required = profit_cooldown_hours
        close_type = "profit"
    elif pnl < 0:
        cooldown_required = loss_cooldown_hours
        close_type = "loss"
    else:
        cooldown_required = flat_cooldown_hours
        close_type = "flat"

    score_ok, score_meta = score_improved_enough(candidate, recent)
    conf_ok, conf_meta = confidence_improved(candidate, recent)
    fresh = _has_fresh_catalyst(candidate)
    same_strategy = bool(recent.get("_guard_same_strategy"))

    result.update({
        "recent_trade_id": _trade_id(recent),
        "recent_close_type": close_type,
        "recent_close_pnl": pnl,
        "hours_since_close": round(hours_since, 4),
        "cooldown_hours_required": cooldown_required,
        "fresh_catalyst": fresh,
        "score_improved": score_ok,
        "confidence_improved": conf_ok,
        "same_strategy": same_strategy,
        "score_meta": score_meta,
        "confidence_meta": conf_meta,
    })

    cooldown_satisfied = hours_since >= cooldown_required
    meaningful_upgrade = score_ok or conf_ok or fresh

    if cooldown_satisfied:
        result.update({
            "allowed": True,
            "status": "CLEAR",
            "reason": "cooldown_satisfied",
            "reason_detail": f"{symbol} had a recent {close_type} close, but the cooldown window has passed.",
            "blocked": False,
            "warning": False,
        })
        return result

    if meaningful_upgrade and close_type == "profit":
        result.update({
            "allowed": True,
            "status": "WATCH",
            "reason": "recent_profit_reentry_allowed_with_upgrade",
            "reason_detail": (
                f"{symbol} closed recently for profit, but the new setup has enough improvement "
                "or a fresh catalyst to allow cautious re-entry."
            ),
            "blocked": False,
            "warning": True,
        })
        return result

    if meaningful_upgrade and close_type == "flat" and not same_strategy:
        result.update({
            "allowed": True,
            "status": "WATCH",
            "reason": "recent_flat_reentry_allowed_with_new_setup",
            "reason_detail": (
                f"{symbol} closed recently flat, but the new setup appears meaningfully different."
            ),
            "blocked": False,
            "warning": True,
        })
        return result

    if close_type == "profit":
        reason = "recent_profit_wait_for_fresh_setup"
        detail = (
            f"{symbol} was closed for profit {round(hours_since, 2)} hours ago. "
            "The Observatory should wait for cooldown, stronger score, stronger confidence, "
            "or a fresh catalyst before re-entering."
        )
    elif close_type == "loss":
        reason = "recent_loss_reentry_blocked"
        detail = (
            f"{symbol} was closed for a loss {round(hours_since, 2)} hours ago. "
            "Re-entry is blocked until the setup materially improves or cooldown passes."
        )
    else:
        reason = "recent_flat_reentry_blocked"
        detail = (
            f"{symbol} was closed recently without a strong outcome. "
            "Re-entry is blocked until a fresher setup appears."
        )

    result.update({
        "allowed": False,
        "status": "BLOCKED",
        "reason": reason,
        "reason_detail": detail,
        "blocked": True,
        "warning": False,
    })

    return result


def apply_reentry_discipline_to_candidate(
    candidate: Dict[str, Any],
    closed_positions: Optional[Iterable[Dict[str, Any]]] = None,
    now: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    row = deepcopy(candidate) if isinstance(candidate, dict) else {}

    guard = evaluate_reentry_discipline(
        row,
        closed_positions=closed_positions,
        now=now,
        **kwargs,
    )

    row["reentry_discipline"] = guard
    row["reentry_discipline_allowed"] = guard.get("allowed")
    row["reentry_discipline_reason"] = guard.get("reason")
    row["reentry_discipline_status"] = guard.get("status")
    row["reentry_discipline_hours_since_close"] = guard.get("hours_since_close")
    row["fresh_catalyst_detected"] = guard.get("fresh_catalyst")

    if not guard.get("allowed", True):
        row["research_approved"] = False
        row["execution_ready"] = False
        row["selected_for_execution"] = False
        row["blocked_at"] = "reentry_discipline_guard"
        row["final_reason"] = guard.get("reason")
        row["final_reason_detail"] = guard.get("reason_detail")

    elif guard.get("status") == "WATCH":
        warnings = row.get("readiness_warnings")
        if not isinstance(warnings, list):
            warnings = []
        warnings.append(guard.get("reason"))
        row["readiness_warnings"] = warnings
        row["reentry_allowed_with_caution"] = True

    return row


def evaluate_candidates(
    candidates: Iterable[Dict[str, Any]],
    closed_positions: Optional[Iterable[Dict[str, Any]]] = None,
    now: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    now = now or _now()
    rows = [row for row in candidates if isinstance(row, dict)]
    closed_rows = list(closed_positions) if closed_positions is not None else load_closed_positions()

    evaluated = [
        apply_reentry_discipline_to_candidate(
            row,
            closed_positions=closed_rows,
            now=now,
            **kwargs,
        )
        for row in rows
    ]

    counts: Dict[str, int] = {}
    blocked_symbols: List[str] = []
    watch_symbols: List[str] = []

    for row in evaluated:
        status = str(row.get("reentry_discipline_status") or "UNKNOWN")
        counts[status] = counts.get(status, 0) + 1

        if status == "BLOCKED":
            blocked_symbols.append(_symbol(row))
        elif status == "WATCH":
            watch_symbols.append(_symbol(row))

    return {
        "evaluated": evaluated,
        "summary": {
            "total": len(evaluated),
            "counts": counts,
            "blocked_symbols": blocked_symbols,
            "watch_symbols": watch_symbols,
            "blocked_count": len(blocked_symbols),
            "watch_count": len(watch_symbols),
            "generated_at": now.isoformat(),
        },
    }


def self_test() -> Dict[str, Any]:
    now = datetime(2026, 5, 22, 14, 30, 0, tzinfo=timezone.utc)

    closed = [
        {
            "symbol": "SNOW",
            "strategy": "CALL",
            "trade_id": "SNOW-CALL-OLD",
            "closed_at": "2026-05-22T14:00:00+00:00",
            "pnl": 55.0,
            "score": 180,
            "confidence": "HIGH",
        },
        {
            "symbol": "MSFT",
            "strategy": "CALL",
            "trade_id": "MSFT-CALL-LOSS",
            "closed_at": "2026-05-22T13:30:00+00:00",
            "pnl": -20.0,
            "score": 160,
            "confidence": "HIGH",
        },
        {
            "symbol": "AAPL",
            "strategy": "CALL",
            "trade_id": "AAPL-CALL-OLD",
            "closed_at": "2026-05-20T10:00:00+00:00",
            "pnl": 15.0,
            "score": 150,
            "confidence": "MEDIUM",
        },
    ]

    candidates = [
        {
            "symbol": "SNOW",
            "strategy": "CALL",
            "score": 185,
            "confidence": "HIGH",
        },
        {
            "symbol": "SNOW",
            "strategy": "CALL",
            "score": 260,
            "confidence": "HIGH",
        },
        {
            "symbol": "MSFT",
            "strategy": "CALL",
            "score": 170,
            "confidence": "HIGH",
        },
        {
            "symbol": "AAPL",
            "strategy": "CALL",
            "score": 170,
            "confidence": "HIGH",
        },
        {
            "symbol": "NVDA",
            "strategy": "CALL",
            "score": 220,
            "confidence": "HIGH",
        },
    ]

    return evaluate_candidates(
        candidates,
        closed_positions=closed,
        now=now,
        profit_cooldown_hours=24.0,
        loss_cooldown_hours=48.0,
        flat_cooldown_hours=18.0,
    )


__all__ = [
    "DEFAULT_PROFIT_COOLDOWN_HOURS",
    "DEFAULT_LOSS_COOLDOWN_HOURS",
    "DEFAULT_FLAT_COOLDOWN_HOURS",
    "load_closed_positions",
    "find_recent_symbol_closes",
    "evaluate_reentry_discipline",
    "apply_reentry_discipline_to_candidate",
    "evaluate_candidates",
    "self_test",
]
