from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


# =========================================================
# Compatibility constants
# =========================================================

MODE_SURVEY = "survey"
MODE_PAPER = "paper"
MODE_LIVE = "live"


# =========================================================
# Helpers
# =========================================================

def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _dedupe_keep_order(items: List[Any]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in items:
        text = _safe_str(item, "")
        if text and text not in seen:
            seen.add(text)
            out.append(text)
    return out


# =========================================================
# Base profiles
# =========================================================

_BASE_HARD_REASONS = [
    "cash_reserve_too_low",
    "governor_blocked:cash_reserve_too_low",
    "reserve_blocked",
    "insufficient_cash_after_reserve",
    "pdt_restricted",
    "governor_blocked:pdt_restricted",
    "max_open_positions",
    "max_open_positions_reached",
    "max_daily_loss_hit",
    "daily_entry_cap",
    "kill_switch",
    "kill_switch_enabled",
    "session_unhealthy",
    "broker_unhealthy",
    "max_drawdown_hit",
]

BASE_MODE_PROFILE: Dict[str, Any] = {
    "mode": MODE_PAPER,
    "mode_label": "Paper Mode",
    "mode_shell": "Solar System",
    "mode_description": (
        "Structured simulation mode. This is the realistic practice layer, "
        "where capital discipline, PDT discipline, and execution protection "
        "are enforced like a live-trading rehearsal."
    ),
    "theme_family": "solar_system",

    # strictness
    "strict_reserve": True,
    "strict_pdt": True,
    "strict_execution_gate": True,
    "strict_position_cap": True,
    "strict_daily_loss": True,
    "strict_drawdown": True,
    "strict_kill_switch": True,

    # warning conversions
    "reserve_warning_only": False,
    "pdt_warning_only": False,
    "execution_warning_only": False,
    "position_cap_warning_only": False,
    "daily_loss_warning_only": False,

    # vehicle behavior
    "allow_stock_fallback": True,
    "options_first": True,
    "allow_same_day_high_risk_contracts": False,
    "minimum_option_dte": 1,

    # capital behavior
    "minimum_stock_cash_buffer_pct": 0.20,
    "minimum_live_like_cash_buffer_pct": 0.20,
    "reserve_floor_pct": 0.20,

    # limits
    "max_daily_entries": 3,
    "max_open_positions": 3,
    "queue_limit": 3,

    # reason helpers
    "soft_block_reasons": [],
    "hard_block_reasons": list(_BASE_HARD_REASONS),
}


SURVEY_MODE_PROFILE: Dict[str, Any] = {
    **BASE_MODE_PROFILE,
    "mode": MODE_SURVEY,
    "mode_label": "Survey Mode",
    "mode_shell": "Deep Space",
    "mode_description": (
        "Exploratory simulation mode. This is the looser research layer where "
        "the system can surface more ideas, with most hard blocks softened into warnings."
    ),
    "theme_family": "deep_space",

    "strict_reserve": False,
    "strict_pdt": False,
    "strict_execution_gate": False,
    "strict_position_cap": False,
    "strict_daily_loss": False,
    "strict_drawdown": False,
    "strict_kill_switch": False,

    "reserve_warning_only": True,
    "pdt_warning_only": True,
    "execution_warning_only": True,
    "position_cap_warning_only": True,
    "daily_loss_warning_only": True,

    "allow_stock_fallback": True,
    "options_first": True,
    "allow_same_day_high_risk_contracts": True,
    "minimum_option_dte": 0,

    "minimum_stock_cash_buffer_pct": 0.00,
    "minimum_live_like_cash_buffer_pct": 0.00,
    "reserve_floor_pct": 0.00,

    "max_daily_entries": 5,
    "max_open_positions": 5,
    "queue_limit": 5,

    "soft_block_reasons": list(_BASE_HARD_REASONS),
    "hard_block_reasons": [],
}


PAPER_MODE_PROFILE: Dict[str, Any] = {
    **BASE_MODE_PROFILE,
    "mode": MODE_PAPER,
    "mode_label": "Paper Mode",
    "mode_shell": "Solar System",
    "mode_description": (
        "Structured simulation mode. This is the realistic practice layer, "
        "where capital discipline is still respected, but some hard live-style "
        "blocks can be softened so users can learn without building reckless habits."
    ),
    "theme_family": "solar_system",

    # relaxed paper mode
    "strict_reserve": False,
    "strict_pdt": False,
    "strict_execution_gate": True,
    "strict_position_cap": True,
    "strict_daily_loss": True,
    "strict_drawdown": True,
    "strict_kill_switch": True,

    "reserve_warning_only": True,
    "pdt_warning_only": True,
    "execution_warning_only": False,
    "position_cap_warning_only": False,
    "daily_loss_warning_only": False,

    "allow_stock_fallback": True,
    "options_first": True,
    "allow_same_day_high_risk_contracts": False,
    "minimum_option_dte": 1,

    "minimum_stock_cash_buffer_pct": 0.10,
    "minimum_live_like_cash_buffer_pct": 0.10,
    "reserve_floor_pct": 0.10,

    "max_daily_entries": 3,
    "max_open_positions": 3,
    "queue_limit": 3,

    "soft_block_reasons": [
        "cash_reserve_too_low",
        "governor_blocked:cash_reserve_too_low",
        "reserve_blocked",
        "insufficient_cash_after_reserve",
        "pdt_restricted",
        "governor_blocked:pdt_restricted",
    ],
    "hard_block_reasons": [
        "max_open_positions",
        "max_open_positions_reached",
        "max_daily_loss_hit",
        "daily_entry_cap",
        "kill_switch",
        "kill_switch_enabled",
        "session_unhealthy",
        "broker_unhealthy",
        "max_drawdown_hit",
    ],
}


LIVE_MODE_PROFILE: Dict[str, Any] = {
    **BASE_MODE_PROFILE,
    "mode": MODE_LIVE,
    "mode_label": "Live Mode",
    "mode_shell": "Observatory",
    "mode_description": (
        "Live execution mode. This is the highest-stakes layer where protections "
        "remain strict and capital preservation comes first."
    ),
    "theme_family": "observatory",

    "strict_reserve": True,
    "strict_pdt": True,
    "strict_execution_gate": True,
    "strict_position_cap": True,
    "strict_daily_loss": True,
    "strict_drawdown": True,
    "strict_kill_switch": True,

    "reserve_warning_only": False,
    "pdt_warning_only": False,
    "execution_warning_only": False,
    "position_cap_warning_only": False,
    "daily_loss_warning_only": False,

    "allow_stock_fallback": True,
    "options_first": True,
    "allow_same_day_high_risk_contracts": False,
    "minimum_option_dte": 1,

    "minimum_stock_cash_buffer_pct": 0.20,
    "minimum_live_like_cash_buffer_pct": 0.20,
    "reserve_floor_pct": 0.20,

    "max_daily_entries": 3,
    "max_open_positions": 3,
    "queue_limit": 3,

    "soft_block_reasons": [],
    "hard_block_reasons": list(_BASE_HARD_REASONS),
}


MODE_PROFILES: Dict[str, Dict[str, Any]] = {
    MODE_SURVEY: SURVEY_MODE_PROFILE,
    MODE_PAPER: PAPER_MODE_PROFILE,
    MODE_LIVE: LIVE_MODE_PROFILE,
}


# =========================================================
# Mode resolution
# =========================================================

def normalize_mode(mode: Any) -> str:
    text = _safe_str(mode, MODE_PAPER).lower()

    aliases = {
        "survey": MODE_SURVEY,
        "deep_space": MODE_SURVEY,
        "exploratory": MODE_SURVEY,
        "explore": MODE_SURVEY,

        "paper": MODE_PAPER,
        "paper_mode": MODE_PAPER,
        "sim": MODE_PAPER,
        "simulation": MODE_PAPER,
        "practice": MODE_PAPER,

        "live": MODE_LIVE,
        "live_mode": MODE_LIVE,
        "real": MODE_LIVE,
        "production": MODE_LIVE,
    }

    return aliases.get(text, MODE_PAPER)


def build_mode_context(mode: Any = MODE_PAPER) -> Dict[str, Any]:
    normalized = normalize_mode(mode)
    profile = MODE_PROFILES.get(normalized, PAPER_MODE_PROFILE)
    out = deepcopy(profile)
    out["mode"] = normalized
    out["soft_block_reasons"] = _dedupe_keep_order(_safe_list(out.get("soft_block_reasons", [])))
    out["hard_block_reasons"] = _dedupe_keep_order(_safe_list(out.get("hard_block_reasons", [])))
    return out


# =========================================================
# Compatibility wrappers
# =========================================================

def get_mode_profile(mode: Any = MODE_PAPER) -> Dict[str, Any]:
    return build_mode_context(mode)


def get_mode_config(mode: Any = MODE_PAPER) -> Dict[str, Any]:
    return build_mode_context(mode)


def build_mode_payload(mode: Any = MODE_PAPER) -> Dict[str, Any]:
    return build_mode_context(mode)


# =========================================================
# Reason classification
# =========================================================

def classify_reason_for_mode(reason: Any, mode: Any = MODE_PAPER) -> str:
    text = _safe_str(reason, "")
    context = build_mode_context(mode)

    soft_reasons = set(_safe_list(context.get("soft_block_reasons", [])))
    hard_reasons = set(_safe_list(context.get("hard_block_reasons", [])))

    if text in soft_reasons:
        return "warning"
    if text in hard_reasons:
        return "blocked"

    # default behavior: if the mode is warning-only on execution, soften unknown execution blocks
    if bool(context.get("execution_warning_only", False)):
        return "warning"

    return "blocked"


# =========================================================
# Governor / execution guard adapters
# =========================================================

def apply_mode_to_governor(governor: Dict[str, Any], mode: Any = None) -> Dict[str, Any]:
    governor = _safe_dict(governor)
    current_mode = mode if mode is not None else governor.get("trading_mode", MODE_PAPER)
    context = build_mode_context(current_mode)

    governor["trading_mode"] = context["mode"]
    governor["mode_context"] = context
    governor.setdefault("reasons", [])
    governor.setdefault("warnings", [])
    governor.setdefault("status_label", "OK")
    governor.setdefault("blocked", False)
    governor.setdefault("ok_to_trade", not governor.get("blocked", False))

    return governor


def apply_mode_to_execution_guard(guard: Dict[str, Any], mode: Any = None) -> Dict[str, Any]:
    guard = _safe_dict(guard)
    current_mode = mode if mode is not None else guard.get("trading_mode", MODE_PAPER)
    context = build_mode_context(current_mode)

    reason = _safe_str(guard.get("reason", ""), "")
    classification = classify_reason_for_mode(reason, context["mode"])

    guard["trading_mode"] = context["mode"]
    guard["mode_context"] = context

    if reason:
        if classification == "warning":
            guard["blocked"] = False
            guard["warning"] = reason
            guard["warning_reason"] = reason
            guard["classification"] = "warning"
        else:
            guard["blocked"] = bool(guard.get("blocked", True))
            guard["classification"] = "blocked"
    else:
        guard["classification"] = "clear"
        guard["blocked"] = bool(guard.get("blocked", False))

    return guard
