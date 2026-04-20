from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


BASE_MODE_PROFILE: Dict[str, Any] = {
    "mode": "paper",
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

    # optional post-processing helpers
    "soft_block_reasons": [],
    "hard_block_reasons": [
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
    ],
}


SURVEY_MODE_PROFILE: Dict[str, Any] = {
    **BASE_MODE_PROFILE,
    "mode": "survey",
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

    "soft_block_reasons": [
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
    ],
    "hard_block_reasons": [],
}


PAPER_MODE_PROFILE: Dict[str, Any] = {
    **BASE_MODE_PROFILE,
    "mode": "paper",
    "mode_label": "Paper Mode",
    "mode_shell": "Solar System",
    "mode_description": (
        "Structured simulation mode. This is the realistic practice layer, "
        "where capital discipline is still respected, but some hard live-style "
        "blocks can be softened so users can learn without building reckless habits."
    ),
    "theme_family": "solar_system",

    # Relaxed paper mode
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
    "mode": "live",
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
    "hard_block_reasons": [
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
    ],
}


MODE_PROFILES: Dict[str, Dict[str, Any]] = {
    "survey": SURVEY_MODE_PROFILE,
    "paper": PAPER_MODE_PROFILE,
    "live": LIVE_MODE_PROFILE,
}


def normalize_mode(mode: Any) -> str:
    text = _safe_str(mode, "paper").lower()

    aliases = {
        "survey": "survey",
        "deep_space": "survey",
        "exploratory": "survey",

        "paper": "paper",
        "paper_mode": "paper",
        "sim": "paper",
        "simulation": "paper",

        "live": "live",
        "live_mode": "live",
        "real": "live",
    }

    return aliases.get(text, "paper")


def build_mode_context(mode: Any = "paper") -> Dict[str, Any]:
    normalized = normalize_mode(mode)
    profile = MODE_PROFILES.get(normalized, PAPER_MODE_PROFILE)
    return deepcopy(profile)


def apply_mode_to_governor(governor: Dict[str, Any], mode: Any = None) -> Dict[str, Any]:
    governor = governor if isinstance(governor, dict) else {}
    current_mode = mode if mode is not None else governor.get("trading_mode", "paper")
    context = build_mode_context(current_mode)

    governor["trading_mode"] = context["mode"]
    governor["mode_context"] = context
    return governor


def get_mode_profile(mode: Any = "paper") -> Dict[str, Any]:
    return build_mode_context(mode)
