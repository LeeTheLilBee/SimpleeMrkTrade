from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List

MODE_SURVEY = "survey"
MODE_PAPER = "paper"
MODE_LIVE = "live"

SHELL_DEEP_SPACE = "Deep Space"
SHELL_SOLAR_SYSTEM = "Solar System"
SHELL_OBSERVATORY = "Observatory"


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value).strip()
        return text if text else default
    except Exception:
        return default


def _safe_bool(value: Any, default: bool = False) -> bool:
    try:
        return bool(value)
    except Exception:
        return bool(default)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return int(default)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _safe_list(value: Any) -> List[Any]:
    return list(value) if isinstance(value, list) else []


def _safe_dict(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


MODE_PROFILES: Dict[str, Dict[str, Any]] = {
    MODE_SURVEY: {
        "mode": MODE_SURVEY,
        "label": "Survey Mode",
        "shell": SHELL_DEEP_SPACE,
        "description": (
            "Exploratory simulation mode. The system still evaluates risk, but softer "
            "constraints like reserve, PDT, and execution gating can warn instead of block."
        ),
        "theme_family": "deep_space",

        # strictness
        "strict_reserve": False,
        "strict_pdt": False,
        "strict_execution_gate": False,
        "strict_position_cap": False,
        "strict_daily_loss": False,
        "strict_drawdown": False,
        "strict_kill_switch": True,

        # warning behavior
        "reserve_warning_only": True,
        "pdt_warning_only": True,
        "execution_warning_only": True,
        "position_cap_warning_only": True,
        "daily_loss_warning_only": True,

        # vehicle / execution behavior
        "allow_stock_fallback": True,
        "options_first": True,
        "allow_same_day_high_risk_contracts": True,
        "minimum_option_dte": 0,

        # cash / reserve behavior
        "minimum_stock_cash_buffer_pct": 0.05,
        "minimum_live_like_cash_buffer_pct": 0.05,
        "reserve_floor_pct": 0.05,

        # queue / capacity
        "max_daily_entries": 6,
        "max_open_positions": 6,
        "queue_limit": 6,

        # reason groupings
        "soft_block_reasons": [
            "cash_reserve_too_low",
            "governor_blocked:cash_reserve_too_low",
            "reserve_blocked",
            "insufficient_cash_after_reserve",
            "pdt_restricted",
            "max_open_positions",
            "max_open_positions_reached",
            "max_daily_loss_hit",
            "daily_entry_cap",
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
        "label": "Paper Mode",
        "shell": SHELL_SOLAR_SYSTEM,
        "description": (
            "Structured simulation mode. This is the realistic practice layer, where "
            "capital discipline matters and execution protection is mostly enforced."
        ),
        "theme_family": "solar_system",

        # strictness
        "strict_reserve": True,
        "strict_pdt": False,
        "strict_execution_gate": True,
        "strict_position_cap": True,
        "strict_daily_loss": True,
        "strict_drawdown": True,
        "strict_kill_switch": True,

        # warning behavior
        "reserve_warning_only": False,
        "pdt_warning_only": True,
        "execution_warning_only": False,
        "position_cap_warning_only": False,
        "daily_loss_warning_only": False,

        # vehicle / execution behavior
        "allow_stock_fallback": True,
        "options_first": True,
        "allow_same_day_high_risk_contracts": False,
        "minimum_option_dte": 1,

        # cash / reserve behavior
        "minimum_stock_cash_buffer_pct": 0.20,
        "minimum_live_like_cash_buffer_pct": 0.20,
        "reserve_floor_pct": 0.20,

        # queue / capacity
        "max_daily_entries": 3,
        "max_open_positions": 3,
        "queue_limit": 3,

        # reason groupings
        "soft_block_reasons": [
            "pdt_restricted",
        ],
        "hard_block_reasons": [
            "cash_reserve_too_low",
            "governor_blocked:cash_reserve_too_low",
            "reserve_blocked",
            "insufficient_cash_after_reserve",
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
        "label": "Live Mode",
        "shell": SHELL_OBSERVATORY,
        "description": (
            "Real-money mode. Full discipline and protection rules are enforced."
        ),
        "theme_family": "observatory",

        # strictness
        "strict_reserve": True,
        "strict_pdt": True,
        "strict_execution_gate": True,
        "strict_position_cap": True,
        "strict_daily_loss": True,
        "strict_drawdown": True,
        "strict_kill_switch": True,

        # warning behavior
        "reserve_warning_only": False,
        "pdt_warning_only": False,
        "execution_warning_only": False,
        "position_cap_warning_only": False,
        "daily_loss_warning_only": False,

        # vehicle / execution behavior
        "allow_stock_fallback": True,
        "options_first": True,
        "allow_same_day_high_risk_contracts": False,
        "minimum_option_dte": 1,

        # cash / reserve behavior
        "minimum_stock_cash_buffer_pct": 0.20,
        "minimum_live_like_cash_buffer_pct": 0.20,
        "reserve_floor_pct": 0.20,

        # queue / capacity
        "max_daily_entries": 3,
        "max_open_positions": 3,
        "queue_limit": 3,

        # reason groupings
        "soft_block_reasons": [],
        "hard_block_reasons": [
            "cash_reserve_too_low",
            "governor_blocked:cash_reserve_too_low",
            "reserve_blocked",
            "insufficient_cash_after_reserve",
            "pdt_restricted",
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


def normalize_mode(value: Any = None) -> str:
    raw = _safe_str(value, "").lower()
    if raw in {"survey", "survey_mode", "explore", "exploration", "deep_space"}:
        return MODE_SURVEY
    if raw in {"live", "real", "production", "prod", "observatory"}:
        return MODE_LIVE
    return MODE_PAPER


def get_mode_profile(mode: Any = None) -> Dict[str, Any]:
    normalized = normalize_mode(mode)
    base = MODE_PROFILES.get(normalized, MODE_PROFILES[MODE_PAPER])
    return deepcopy(base)


def get_mode_config(mode: Any = None) -> Dict[str, Any]:
    return get_mode_profile(mode)


def get_mode_label(mode: Any = None) -> str:
    return _safe_str(get_mode_profile(mode).get("label"), "Paper Mode")


def get_mode_shell(mode: Any = None) -> str:
    return _safe_str(get_mode_profile(mode).get("shell"), SHELL_SOLAR_SYSTEM)


def get_mode_theme_family(mode: Any = None) -> str:
    return _safe_str(get_mode_profile(mode).get("theme_family"), "solar_system")


def build_mode_context(mode: Any = None) -> Dict[str, Any]:
    profile = get_mode_profile(mode)
    return {
        "mode": profile["mode"],
        "mode_label": profile["label"],
        "mode_shell": profile["shell"],
        "mode_description": profile["description"],
        "theme_family": profile["theme_family"],

        "strict_reserve": _safe_bool(profile.get("strict_reserve", True), True),
        "strict_pdt": _safe_bool(profile.get("strict_pdt", True), True),
        "strict_execution_gate": _safe_bool(profile.get("strict_execution_gate", True), True),
        "strict_position_cap": _safe_bool(profile.get("strict_position_cap", True), True),
        "strict_daily_loss": _safe_bool(profile.get("strict_daily_loss", True), True),
        "strict_drawdown": _safe_bool(profile.get("strict_drawdown", True), True),
        "strict_kill_switch": _safe_bool(profile.get("strict_kill_switch", True), True),

        "reserve_warning_only": _safe_bool(profile.get("reserve_warning_only", False), False),
        "pdt_warning_only": _safe_bool(profile.get("pdt_warning_only", False), False),
        "execution_warning_only": _safe_bool(profile.get("execution_warning_only", False), False),
        "position_cap_warning_only": _safe_bool(profile.get("position_cap_warning_only", False), False),
        "daily_loss_warning_only": _safe_bool(profile.get("daily_loss_warning_only", False), False),

        "allow_stock_fallback": _safe_bool(profile.get("allow_stock_fallback", True), True),
        "options_first": _safe_bool(profile.get("options_first", True), True),
        "max_daily_entries": _safe_int(profile.get("max_daily_entries", 3), 3),
        "max_open_positions": _safe_int(profile.get("max_open_positions", 3), 3),
        "queue_limit": _safe_int(profile.get("queue_limit", 3), 3),

        "allow_same_day_high_risk_contracts": _safe_bool(
            profile.get("allow_same_day_high_risk_contracts", False),
            False,
        ),
        "minimum_option_dte": _safe_int(profile.get("minimum_option_dte", 1), 1),
        "minimum_stock_cash_buffer_pct": _safe_float(
            profile.get("minimum_stock_cash_buffer_pct", 0.20),
            0.20,
        ),
        "minimum_live_like_cash_buffer_pct": _safe_float(
            profile.get("minimum_live_like_cash_buffer_pct", 0.20),
            0.20,
        ),
        "reserve_floor_pct": _safe_float(profile.get("reserve_floor_pct", 0.20), 0.20),

        "soft_block_reasons": _safe_list(profile.get("soft_block_reasons")),
        "hard_block_reasons": _safe_list(profile.get("hard_block_reasons")),
    }


def build_mode_payload(mode: Any = None) -> Dict[str, Any]:
    return build_mode_context(mode)


def is_survey_mode(mode: Any = None) -> bool:
    return normalize_mode(mode) == MODE_SURVEY


def is_paper_mode(mode: Any = None) -> bool:
    return normalize_mode(mode) == MODE_PAPER


def is_live_mode(mode: Any = None) -> bool:
    return normalize_mode(mode) == MODE_LIVE


def classify_reason_for_mode(reason: Any, mode: Any = None) -> str:
    reason_text = _safe_str(reason, "")
    context = build_mode_context(mode)
    soft = set(_safe_list(context.get("soft_block_reasons")))
    hard = set(_safe_list(context.get("hard_block_reasons")))
    if reason_text in hard:
        return "hard"
    if reason_text in soft:
        return "soft"
    return "neutral"


def soften_reasons_for_mode(
    reasons: List[Any],
    warnings: List[Any],
    mode: Any = None,
) -> Dict[str, List[str]]:
    context = build_mode_context(mode)
    strict_execution_gate = _safe_bool(context.get("strict_execution_gate", True), True)

    normalized_reasons: List[str] = []
    normalized_warnings: List[str] = []

    seen_reasons = set()
    seen_warnings = set()

    for item in _safe_list(reasons):
        text = _safe_str(item, "")
        if not text:
            continue
        classification = classify_reason_for_mode(text, context.get("mode"))
        if classification == "soft" and not strict_execution_gate:
            if text not in seen_warnings:
                normalized_warnings.append(text)
                seen_warnings.add(text)
        else:
            if text not in seen_reasons:
                normalized_reasons.append(text)
                seen_reasons.add(text)

    for item in _safe_list(warnings):
        text = _safe_str(item, "")
        if text and text not in seen_warnings:
            normalized_warnings.append(text)
            seen_warnings.add(text)

    return {
        "reasons": normalized_reasons,
        "warnings": normalized_warnings,
    }


def apply_mode_to_governor(governor: Any, mode: Any = None) -> Dict[str, Any]:
    governor = _safe_dict(governor)
    context = build_mode_context(mode or governor.get("trading_mode") or governor.get("mode"))

    original_reasons = _safe_list(governor.get("reasons"))
    original_warnings = _safe_list(governor.get("warnings"))
    controls = _safe_dict(governor.get("controls"))
    pdt = _safe_dict(governor.get("pdt"))

    softened = soften_reasons_for_mode(
        reasons=original_reasons,
        warnings=original_warnings,
        mode=context.get("mode"),
    )

    reasons = softened["reasons"]
    warnings = softened["warnings"]

    controls["cash_reserve_warning_only"] = (
        controls.get("cash_reserve_too_low", False)
        and classify_reason_for_mode("cash_reserve_too_low", context.get("mode")) == "soft"
        and not _safe_bool(context.get("strict_execution_gate", True), True)
    )
    controls["pdt_warning_only"] = (
        controls.get("pdt_restricted", False)
        and classify_reason_for_mode("pdt_restricted", context.get("mode")) == "soft"
    )
    controls["position_cap_warning_only"] = (
        controls.get("max_open_positions", False)
        and classify_reason_for_mode("max_open_positions", context.get("mode")) == "soft"
        and not _safe_bool(context.get("strict_execution_gate", True), True)
    )
    controls["daily_loss_warning_only"] = (
        controls.get("max_daily_loss_hit", False)
        and classify_reason_for_mode("max_daily_loss_hit", context.get("mode")) == "soft"
        and not _safe_bool(context.get("strict_execution_gate", True), True)
    )

    blocked = len(reasons) > 0

    if blocked:
        status_label = "BLOCKED"
    elif warnings:
        status_label = "CLEAR_WITH_WARNINGS"
    else:
        status_label = "CLEAR"

    governor["reasons"] = reasons
    governor["warnings"] = warnings
    governor["controls"] = controls
    governor["pdt"] = pdt
    governor["trading_mode"] = context["mode"]
    governor["mode_context"] = context
    governor["blocked"] = blocked
    governor["ok_to_trade"] = not blocked
    governor["status_label"] = status_label

    return governor


def apply_mode_to_execution_guard(exec_guard: Any, mode: Any = None) -> Dict[str, Any]:
    guard = _safe_dict(exec_guard)
    context = build_mode_context(mode or guard.get("trading_mode") or guard.get("mode"))

    reason = _safe_str(guard.get("reason"), "")
    warnings = _safe_list(guard.get("warnings"))
    blocked = _safe_bool(guard.get("blocked"), False)

    if blocked:
        classification = classify_reason_for_mode(reason, context.get("mode"))
        strict_execution_gate = _safe_bool(context.get("strict_execution_gate", True), True)

        if classification == "soft" and not strict_execution_gate:
            if reason and reason not in warnings:
                warnings.append(reason)
            guard["blocked"] = False
            guard["warning_only"] = True
            guard["warnings"] = warnings
            guard["status_label"] = "WARNING"
        else:
            guard["warning_only"] = False
            guard["warnings"] = warnings
            guard["status_label"] = "BLOCKED"
    else:
        guard["warning_only"] = False
        guard["warnings"] = warnings
        guard["status_label"] = "OK" if not warnings else "OK_WITH_WARNINGS"

    guard["trading_mode"] = context["mode"]
    guard["mode_context"] = context
    return guard


def resolve_governor_for_mode(governor: Any, mode: Any = None) -> Dict[str, Any]:
    return apply_mode_to_governor(governor, mode)


def resolve_execution_guard_for_mode(exec_guard: Any, mode: Any = None) -> Dict[str, Any]:
    return apply_mode_to_execution_guard(exec_guard, mode)
