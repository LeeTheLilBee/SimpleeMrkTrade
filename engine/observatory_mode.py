from __future__ import annotations

MODE_SURVEY = "survey"
MODE_PAPER = "paper"
MODE_LIVE = "live"

SHELL_DEEP_SPACE = "Deep Space"
SHELL_SOLAR_SYSTEM = "Solar System"
SHELL_OBSERVATORY = "Observatory"


def _safe_str(value, default=""):
    try:
        text = str(value).strip()
        return text if text else default
    except Exception:
        return default


def _safe_bool(value, default=False):
    try:
        return bool(value)
    except Exception:
        return bool(default)


def _safe_list(value):
    return value if isinstance(value, list) else []


def _safe_dict(value):
    return value if isinstance(value, dict) else {}


MODE_PROFILES = {
    MODE_SURVEY: {
        "mode": MODE_SURVEY,
        "label": "Survey Mode",
        "shell": SHELL_DEEP_SPACE,
        "description": (
            "Exploratory simulation mode. The system still evaluates risk, but softer "
            "constraints like reserve, PDT, and execution gating can warn instead of block."
        ),
        "strict_reserve": False,
        "strict_pdt": False,
        "strict_execution_gate": False,
        "reserve_warning_only": True,
        "pdt_warning_only": True,
        "execution_warning_only": True,
        "theme_family": "deep_space",
    },
    MODE_PAPER: {
        "mode": MODE_PAPER,
        "label": "Paper Mode",
        "shell": SHELL_SOLAR_SYSTEM,
        "description": (
            "Structured simulation mode. This is the realistic practice layer, where "
            "capital discipline still matters, but some compliance-style checks can remain warnings."
        ),
        "strict_reserve": True,
        "strict_pdt": False,
        "strict_execution_gate": True,
        "reserve_warning_only": False,
        "pdt_warning_only": True,
        "execution_warning_only": False,
        "theme_family": "solar_system",
    },
    MODE_LIVE: {
        "mode": MODE_LIVE,
        "label": "Live Mode",
        "shell": SHELL_OBSERVATORY,
        "description": (
            "Real-money mode. Full discipline and protection rules are enforced."
        ),
        "strict_reserve": True,
        "strict_pdt": True,
        "strict_execution_gate": True,
        "reserve_warning_only": False,
        "pdt_warning_only": False,
        "execution_warning_only": False,
        "theme_family": "observatory",
    },
}


def normalize_mode(value=None) -> str:
    raw = str(value or "").strip().lower()
    if raw in {"survey", "survey_mode", "explore", "exploration", "deep_space"}:
        return MODE_SURVEY
    if raw in {"live", "real", "production", "prod", "observatory"}:
        return MODE_LIVE
    return MODE_PAPER


def get_mode_profile(mode=None) -> dict:
    normalized = normalize_mode(mode)
    return dict(MODE_PROFILES.get(normalized, MODE_PROFILES[MODE_PAPER]))


def get_mode_config(mode=None) -> dict:
    return get_mode_profile(mode)


def get_mode_label(mode=None) -> str:
    return get_mode_profile(mode).get("label", "Paper Mode")


def get_mode_shell(mode=None) -> str:
    return get_mode_profile(mode).get("shell", SHELL_SOLAR_SYSTEM)


def get_mode_theme_family(mode=None) -> str:
    return get_mode_profile(mode).get("theme_family", "solar_system")


def build_mode_context(mode=None) -> dict:
    profile = get_mode_profile(mode)
    return {
        "mode": profile["mode"],
        "mode_label": profile["label"],
        "mode_shell": profile["shell"],
        "mode_description": profile["description"],
        "theme_family": profile["theme_family"],
        "strict_reserve": bool(profile.get("strict_reserve", True)),
        "strict_pdt": bool(profile.get("strict_pdt", True)),
        "strict_execution_gate": bool(profile.get("strict_execution_gate", True)),
        "reserve_warning_only": bool(profile.get("reserve_warning_only", False)),
        "pdt_warning_only": bool(profile.get("pdt_warning_only", False)),
        "execution_warning_only": bool(profile.get("execution_warning_only", False)),
    }


def build_mode_payload(mode=None) -> dict:
    return build_mode_context(mode)


def is_survey_mode(mode=None) -> bool:
    return normalize_mode(mode) == MODE_SURVEY


def is_paper_mode(mode=None) -> bool:
    return normalize_mode(mode) == MODE_PAPER


def is_live_mode(mode=None) -> bool:
    return normalize_mode(mode) == MODE_LIVE


def apply_mode_to_governor(governor, mode=None) -> dict:
    governor = dict(governor) if isinstance(governor, dict) else {}
    context = build_mode_context(mode)

    reasons = _safe_list(governor.get("reasons", []))
    warnings = _safe_list(governor.get("warnings", []))
    controls = _safe_dict(governor.get("controls", {}))
    pdt = _safe_dict(governor.get("pdt", {}))

    cash_reserve_hit = bool(controls.get("cash_reserve_too_low", False))
    pdt_hit = bool(controls.get("pdt_restricted", False))

    reserve_warning_only = bool(context.get("reserve_warning_only", False))
    pdt_warning_only = bool(context.get("pdt_warning_only", False))

    if cash_reserve_hit and reserve_warning_only:
        reasons = [r for r in reasons if r != "cash_reserve_too_low"]
        if "cash_reserve_too_low" not in warnings:
            warnings.append("cash_reserve_too_low")
        controls["cash_reserve_warning_only"] = True
    else:
        controls["cash_reserve_warning_only"] = False

    if pdt_hit and pdt_warning_only:
        reasons = [r for r in reasons if r != "pdt_restricted"]
        mode_name = context.get("mode", MODE_PAPER)
        warning_label = f"pdt_restricted_{mode_name}_mode"
        if warning_label not in warnings:
            warnings.append(warning_label)
        controls["pdt_warning_only"] = True
    else:
        controls["pdt_warning_only"] = False

    governor["reasons"] = reasons
    governor["warnings"] = warnings
    governor["controls"] = controls
    governor["pdt"] = pdt
    governor["trading_mode"] = context["mode"]
    governor["mode_context"] = context

    blocked = len(reasons) > 0
    governor["blocked"] = blocked
    governor["ok_to_trade"] = not blocked

    if blocked:
        governor["status_label"] = "BLOCKED"
    elif warnings:
        governor["status_label"] = "CLEAR_WITH_WARNINGS"
    else:
        governor["status_label"] = "CLEAR"

    return governor


def apply_mode_to_execution_guard(exec_guard, mode=None) -> dict:
    guard = dict(exec_guard) if isinstance(exec_guard, dict) else {}
    context = build_mode_context(mode)

    blocked = bool(guard.get("blocked", False))
    reason = _safe_str(guard.get("reason", ""), "")
    warnings = _safe_list(guard.get("warnings", []))
    execution_warning_only = bool(context.get("execution_warning_only", False))

    survey_soft_reasons = {
        "cash_reserve_too_low",
        "governor_blocked:cash_reserve_too_low",
        "reserve_blocked",
        "insufficient_cash_after_reserve",
    }

    if blocked and execution_warning_only and reason in survey_soft_reasons:
        if reason and reason not in warnings:
            warnings.append(reason)
        guard["blocked"] = False
        guard["warning_only"] = True
        guard["warnings"] = warnings
        guard["reason"] = reason or "warning_only_execution_guard"
        guard["status_label"] = "WARNING"
        return guard

    guard["warning_only"] = False
    guard["warnings"] = warnings
    guard["status_label"] = "BLOCKED" if blocked else "OK"
    return guard


def resolve_governor_for_mode(governor, mode=None) -> dict:
    return apply_mode_to_governor(governor, mode)


def resolve_execution_guard_for_mode(exec_guard, mode=None) -> dict:
    return apply_mode_to_execution_guard(exec_guard, mode)
