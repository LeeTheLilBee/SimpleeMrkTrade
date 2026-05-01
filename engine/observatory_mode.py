from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional


MODE_SURVEY = "survey"
MODE_PAPER = "paper"
MODE_LIVE = "live"

ALL_MODES = {MODE_SURVEY, MODE_PAPER, MODE_LIVE}


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


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return int(default)
        return int(float(value))
    except Exception:
        return int(default)


def normalize_mode(value: Any) -> str:
    text = _safe_str(value, MODE_PAPER).lower()

    aliases = {
        "survey": MODE_SURVEY,
        "deep_space": MODE_SURVEY,
        "deepspace": MODE_SURVEY,
        "exploratory": MODE_SURVEY,
        "exploration": MODE_SURVEY,

        "paper": MODE_PAPER,
        "paper_mode": MODE_PAPER,
        "paper trading": MODE_PAPER,
        "solar_system": MODE_PAPER,
        "solar": MODE_PAPER,
        "sim": MODE_PAPER,
        "simulation": MODE_PAPER,

        "live": MODE_LIVE,
        "live_mode": MODE_LIVE,
        "observatory": MODE_LIVE,
        "real": MODE_LIVE,
    }

    return aliases.get(text, MODE_PAPER)


_MODE_CONFIGS: Dict[str, Dict[str, Any]] = {
    MODE_SURVEY: {
        "mode": MODE_SURVEY,
        "mode_label": "Survey Mode",
        "mode_shell": "Deep Space",
        "mode_description": (
            "Exploratory simulation mode. This is the looser discovery layer where "
            "the system can study more setups, tolerate more soft warnings, and learn "
            "without pretending every idea deserves live-style rigidity."
        ),
        "theme_family": "deep_space",

        "strict_reserve": False,
        "strict_pdt": False,
        "strict_execution_gate": False,
        "strict_position_cap": False,
        "strict_daily_loss": False,
        "strict_drawdown": False,
        "strict_kill_switch": True,

        "reserve_warning_only": True,
        "pdt_warning_only": True,
        "execution_warning_only": True,
        "position_cap_warning_only": True,
        "daily_loss_warning_only": True,

        "allow_stock_fallback": True,
        "options_first": True,
        "allow_same_day_high_risk_contracts": True,
        "minimum_option_dte": 0,

        "minimum_stock_cash_buffer_pct": 0.05,
        "minimum_live_like_cash_buffer_pct": 0.05,
        "reserve_floor_pct": 0.05,

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
            "max_drawdown_hit",
        ],
        "hard_block_reasons": [
            "kill_switch",
            "kill_switch_enabled",
            "session_unhealthy",
            "broker_unhealthy",
        ],
    },

    MODE_PAPER: {
        "mode": MODE_PAPER,
        "mode_label": "Paper Mode",
        "mode_shell": "Solar System",
        "mode_description": (
            "Structured simulation mode. This is the realistic practice layer, where "
            "capital discipline is still respected, but some hard live-style blocks can "
            "be softened so users can learn without building reckless habits."
        ),
        "theme_family": "solar_system",

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
    },

    MODE_LIVE: {
        "mode": MODE_LIVE,
        "mode_label": "Live Mode",
        "mode_shell": "Observatory",
        "mode_description": (
            "Live capital mode. This is the strictest operating layer, where risk, "
            "reserve protection, broker health, and execution quality are treated as "
            "hard truth instead of advisory guidance."
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
    },
}


def get_mode_config(mode: Any) -> Dict[str, Any]:
    resolved = normalize_mode(mode)
    return deepcopy(_MODE_CONFIGS.get(resolved, _MODE_CONFIGS[MODE_PAPER]))


def build_mode_payload(mode: Any) -> Dict[str, Any]:
    return get_mode_config(mode)


def build_mode_context(mode: Any) -> Dict[str, Any]:
    return get_mode_config(mode)


def classify_reason_for_mode(reason_code: Any, mode: Any) -> str:
    reason = _safe_str(reason_code, "")
    config = get_mode_config(mode)

    if not reason:
        return "unknown"

    if reason in set(_safe_list(config.get("hard_block_reasons"))):
        return "hard"

    if reason in set(_safe_list(config.get("soft_block_reasons"))):
        return "soft"

    generic_hard = {
        "kill_switch",
        "kill_switch_enabled",
        "session_unhealthy",
        "broker_unhealthy",
        "no_buying_power",
        "missing_option_contract",
        "invalid_trade_cost",
        "invalid_stock_payload",
        "research_only_candidate",
        "research_only",
        "missing_lifecycle",
        "storage_failed",
        "execution_handoff_crash",
        "execution_rejected",
        "existing_open_position",
        "already_open_position",
        "max_open_positions_reached",
        "max_open_positions",
        "daily_entry_cap",
        "max_daily_loss_hit",
        "max_drawdown_hit",
    }
    if reason in generic_hard:
        return "hard"

    generic_soft = {
        "cash_reserve_too_low",
        "governor_blocked:cash_reserve_too_low",
        "reserve_blocked",
        "insufficient_cash_after_reserve",
        "pdt_restricted",
        "governor_blocked:pdt_restricted",
    }
    if reason in generic_soft:
        return "soft"

    return "unknown"


def build_mode_metadata(mode: Any) -> Dict[str, Any]:
    config = get_mode_config(mode)
    return {
        "mode": config["mode"],
        "mode_label": config["mode_label"],
        "mode_shell": config["mode_shell"],
        "theme_family": config["theme_family"],
    }


def governor_allows_execution(governor: Dict[str, Any], mode: Any) -> bool:
    governor = _safe_dict(governor)
    resolved_mode = normalize_mode(mode)

    if not governor:
        return False

    if resolved_mode == MODE_SURVEY:
        reasons = set(_safe_list(governor.get("reasons")))
        hard_reasons = {
            "kill_switch",
            "kill_switch_enabled",
            "session_unhealthy",
            "broker_unhealthy",
        }
        return len(reasons.intersection(hard_reasons)) == 0

    return _safe_bool(governor.get("ok_to_trade"), False)


def apply_mode_to_execution_guard(
    guard: Optional[Dict[str, Any]],
    mode: Any,
) -> Dict[str, Any]:
    guard = deepcopy(_safe_dict(guard))
    config = get_mode_config(mode)

    if not guard:
        return {
            "blocked": True,
            "reason": "missing_execution_guard",
            "warnings": [],
            "warning_only": False,
            "status_label": "BLOCKED",
            "trading_mode": config["mode"],
            "mode_context": config,
        }

    reason = _safe_str(guard.get("reason"), "")
    initially_blocked = _safe_bool(guard.get("blocked"), False)

    guard["trading_mode"] = config["mode"]
    guard["mode_context"] = config
    guard["warning_only"] = _safe_bool(guard.get("warning_only"), False)

    if not initially_blocked:
        guard["status_label"] = _safe_str(guard.get("status_label"), "OK")
        return guard

    reason_class = classify_reason_for_mode(reason, config["mode"])
    allow_warning_pass = (
        config["mode"] == MODE_SURVEY
        and _safe_bool(config.get("execution_warning_only"), False)
        and not _safe_bool(config.get("strict_execution_gate"), True)
    )

    if reason_class == "soft" and allow_warning_pass:
        warnings = _safe_list(guard.get("warnings"))
        if reason:
            warnings.append(reason)
        deduped = []
        seen = set()
        for item in warnings:
            text = _safe_str(item, "")
            if text and text not in seen:
                seen.add(text)
                deduped.append(text)

        guard["blocked"] = False
        guard["warning_only"] = True
        guard["warnings"] = deduped
        guard["status_label"] = "WARN"
        if not _safe_str(guard.get("reason"), ""):
            guard["reason"] = "warning_only"

    else:
        guard["blocked"] = True
        guard["status_label"] = "BLOCKED"

    return guard


def mode_requires_strict_reserve(mode: Any) -> bool:
    return _safe_bool(get_mode_config(mode).get("strict_reserve"), False)


def mode_allows_same_day_high_risk_contracts(mode: Any) -> bool:
    return _safe_bool(get_mode_config(mode).get("allow_same_day_high_risk_contracts"), False)


def mode_options_first(mode: Any) -> bool:
    return _safe_bool(get_mode_config(mode).get("options_first"), True)


def mode_allows_stock_fallback(mode: Any) -> bool:
    return _safe_bool(get_mode_config(mode).get("allow_stock_fallback"), True)


__all__ = [
    "MODE_SURVEY",
    "MODE_PAPER",
    "MODE_LIVE",
    "ALL_MODES",
    "normalize_mode",
    "get_mode_config",
    "build_mode_payload",
    "build_mode_context",
    "build_mode_metadata",
    "classify_reason_for_mode",
    "apply_mode_to_execution_guard",
    "governor_allows_execution",
    "mode_requires_strict_reserve",
    "mode_allows_same_day_high_risk_contracts",
    "mode_options_first",
    "mode_allows_stock_fallback",
]
