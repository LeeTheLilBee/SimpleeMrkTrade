from __future__ import annotations

from typing import Any, Dict, List


DEFAULT_ACCOUNT_PROFILES = {
    "default": {
        "account_id": "default",
        "account_name": "Default Paper Account",
        "account_role": "proof_demo",
        "risk_profile": "balanced",
        "purpose": "proof_and_learning",
        "auto_trading_allowed": False,
        "confirm_before_trade": True,
        "options_allowed": True,
        "stocks_allowed": True,
        "max_trade_risk_dollars": 500.0,
        "max_weekly_trades": 3,
        "allow_mirroring": False,
        "priority": 50,
    },
    "trust": {
        "account_id": "trust",
        "account_name": "Trust Account",
        "account_role": "capital_preservation",
        "risk_profile": "conservative",
        "purpose": "preserve_and_compound",
        "auto_trading_allowed": False,
        "confirm_before_trade": True,
        "options_allowed": False,
        "stocks_allowed": True,
        "max_trade_risk_dollars": 250.0,
        "max_weekly_trades": 2,
        "allow_mirroring": False,
        "priority": 90,
    },
    "business_growth": {
        "account_id": "business_growth",
        "account_name": "Business Growth Account",
        "account_role": "growth",
        "risk_profile": "growth",
        "purpose": "controlled_growth",
        "auto_trading_allowed": False,
        "confirm_before_trade": True,
        "options_allowed": True,
        "stocks_allowed": True,
        "max_trade_risk_dollars": 750.0,
        "max_weekly_trades": 4,
        "allow_mirroring": False,
        "priority": 70,
    },
    "research": {
        "account_id": "research",
        "account_name": "Research / Watch Account",
        "account_role": "research_only",
        "risk_profile": "research",
        "purpose": "observe_and_learn",
        "auto_trading_allowed": False,
        "confirm_before_trade": False,
        "options_allowed": False,
        "stocks_allowed": False,
        "max_trade_risk_dollars": 0.0,
        "max_weekly_trades": 0,
        "allow_mirroring": False,
        "priority": 10,
    },
}


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def _safe_bool(value: Any, default: bool = False) -> bool:
    try:
        if value is None:
            return bool(default)
        return bool(value)
    except Exception:
        return bool(default)


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "UNKNOWN").upper()


def _norm_vehicle(value: Any) -> str:
    vehicle = _safe_str(value, "UNKNOWN").upper()
    if vehicle in {"OPTION", "OPTIONS"}:
        return "OPTION"
    if vehicle in {"STOCK", "EQUITY", "SHARES"}:
        return "STOCK"
    if vehicle in {"RESEARCH_ONLY", "WATCH", "OBSERVED_ONLY"}:
        return "RESEARCH_ONLY"
    return vehicle or "UNKNOWN"


def load_default_account_profiles() -> Dict[str, Dict[str, Any]]:
    return {k: dict(v) for k, v in DEFAULT_ACCOUNT_PROFILES.items()}


def _vehicle_allowed_for_account(vehicle: str, profile: Dict[str, Any]) -> bool:
    vehicle = _norm_vehicle(vehicle)

    if vehicle == "OPTION":
        return _safe_bool(profile.get("options_allowed"), False)

    if vehicle == "STOCK":
        return _safe_bool(profile.get("stocks_allowed"), False)

    return False


def _account_role_allows_candidate(candidate: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    vehicle = _norm_vehicle(candidate.get("vehicle_selected", candidate.get("vehicle", "")))
    account_role = _safe_str(profile.get("account_role"), "unknown")
    risk_profile = _safe_str(profile.get("risk_profile"), "balanced")

    score = _safe_float(candidate.get("score", candidate.get("fused_score", 0.0)), 0.0)
    confidence = _safe_str(candidate.get("confidence"), "UNKNOWN").upper()

    if account_role == "research_only":
        return {
            "allowed": False,
            "reason": "account_is_research_only",
            "detail": "This account is designed to observe, not execute.",
        }

    if not _vehicle_allowed_for_account(vehicle, profile):
        return {
            "allowed": False,
            "reason": "vehicle_not_allowed_for_account",
            "detail": f"{vehicle} is not allowed for this account profile.",
        }

    if risk_profile == "conservative":
        if vehicle == "OPTION":
            return {
                "allowed": False,
                "reason": "conservative_account_blocks_options",
                "detail": "Conservative account profile does not accept options exposure.",
            }

        if score < 175 or confidence not in {"HIGH", "VERY_HIGH"}:
            return {
                "allowed": False,
                "reason": "conservative_account_requires_stronger_setup",
                "detail": "Conservative account requires higher-confidence stock-only setups.",
            }

    if risk_profile == "balanced":
        if score < 125:
            return {
                "allowed": False,
                "reason": "balanced_account_score_too_low",
                "detail": "Balanced account requires a stronger setup before routing.",
            }

    if risk_profile == "growth":
        if score < 100:
            return {
                "allowed": False,
                "reason": "growth_account_score_too_low",
                "detail": "Growth account still requires a valid minimum setup.",
            }

    return {
        "allowed": True,
        "reason": "account_role_allows_candidate",
        "detail": "Candidate fits this account profile.",
    }


def route_candidate_to_accounts(
    candidate: Dict[str, Any],
    *,
    account_profiles: Dict[str, Dict[str, Any]] | None = None,
    ecosystem_exposure: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Decides which accounts may receive a candidate.

    Beta-safe rule:
    - This does not execute.
    - It explains why each account did or did not receive the candidate.
    """

    candidate = _safe_dict(candidate)
    profiles = account_profiles or load_default_account_profiles()
    exposure = _safe_dict(ecosystem_exposure)

    symbol = _norm_symbol(candidate.get("symbol"))
    vehicle = _norm_vehicle(candidate.get("vehicle_selected", candidate.get("vehicle", "")))

    routed: List[Dict[str, Any]] = []
    skipped: List[Dict[str, Any]] = []

    existing_symbol_exposure = _safe_list(exposure.get("symbols", {}).get(symbol, [])) if isinstance(exposure.get("symbols"), dict) else []

    for account_id, profile in profiles.items():
        profile = _safe_dict(profile)
        account_id = _safe_str(profile.get("account_id"), account_id)

        role_result = _account_role_allows_candidate(candidate, profile)

        if not role_result.get("allowed"):
            skipped.append({
                "account_id": account_id,
                "account_name": _safe_str(profile.get("account_name"), account_id),
                "allowed": False,
                "reason": role_result.get("reason"),
                "detail": role_result.get("detail"),
            })
            continue

        if existing_symbol_exposure and not _safe_bool(profile.get("allow_mirroring"), False):
            skipped.append({
                "account_id": account_id,
                "account_name": _safe_str(profile.get("account_name"), account_id),
                "allowed": False,
                "reason": "ecosystem_symbol_exposure_exists",
                "detail": (
                    f"{symbol} already appears in ecosystem exposure. "
                    "This account is not allowed to blindly mirror that trade."
                ),
            })
            continue

        if not _safe_bool(profile.get("auto_trading_allowed"), False):
            routed.append({
                "account_id": account_id,
                "account_name": _safe_str(profile.get("account_name"), account_id),
                "allowed": True,
                "route_status": "CONFIRM_BEFORE_TRADE",
                "reason": "manual_confirmation_required",
                "detail": "Candidate fits this account, but auto-trading is not enabled.",
                "priority": _safe_float(profile.get("priority"), 50.0),
            })
            continue

        routed.append({
            "account_id": account_id,
            "account_name": _safe_str(profile.get("account_name"), account_id),
            "allowed": True,
            "route_status": "AUTO_ELIGIBLE",
            "reason": "account_matched_candidate",
            "detail": "Candidate fits this account and auto-trading is enabled.",
            "priority": _safe_float(profile.get("priority"), 50.0),
        })

    routed.sort(key=lambda row: row.get("priority", 0), reverse=True)

    if routed:
        headline = "Candidate matched at least one account."
    else:
        headline = "Candidate did not match any execution account."

    return {
        "symbol": symbol,
        "vehicle": vehicle,
        "headline": headline,
        "routed": routed,
        "skipped": skipped,
        "selected_account": routed[0] if routed else None,
        "why_this_account": routed[0].get("detail") if routed else "No account accepted this candidate.",
    }


def print_account_route(candidate: Dict[str, Any]) -> Dict[str, Any]:
    result = route_candidate_to_accounts(candidate)

    print("ACCOUNT ROUTER")
    print("Symbol:", result.get("symbol"))
    print("Vehicle:", result.get("vehicle"))
    print("Headline:", result.get("headline"))

    selected = result.get("selected_account")
    if selected:
        print("Selected:", selected.get("account_name"), "|", selected.get("route_status"), "|", selected.get("reason"))
    else:
        print("Selected: None")

    if result.get("skipped"):
        print("Skipped:")
        for row in result["skipped"][:10]:
            print("-", row.get("account_name"), "|", row.get("reason"))

    return result


__all__ = [
    "load_default_account_profiles",
    "route_candidate_to_accounts",
    "print_account_route",
]
