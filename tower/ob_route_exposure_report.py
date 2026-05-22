
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _route_methods(rule) -> List[str]:
    try:
        methods = sorted(m for m in (rule.methods or set()) if m not in {"HEAD", "OPTIONS"})
        return methods
    except Exception:
        return []


def build_ob_route_exposure_report(app=None) -> Dict[str, Any]:
    from tower.ob_route_guard import match_ob_guard_policy

    if app is None:
        from web.app import app as flask_app
        app = flask_app

    routes = []
    counts = {
        "total": 0,
        "public_safe": 0,
        "guarded": 0,
        "dynamic_guarded": 0,
        "unmapped_default_deny": 0,
        "tower_owned": 0,
        "static_or_asset": 0,
    }

    for rule in sorted(app.url_map.iter_rules(), key=lambda r: str(r.rule)):
        route = str(rule.rule)
        endpoint = _safe_str(getattr(rule, "endpoint", ""))
        methods = _route_methods(rule)

        if route.startswith("/static") or endpoint == "static":
            category = "static_or_asset"
            match = {"match_type": "static_or_asset", "policy": {"public_allowed": True}}
        elif route == "/tower" or route.startswith("/tower/"):
            category = "tower_owned"
            match = {"match_type": "tower_owned", "policy": {"public_allowed": False, "plain": "Tower owns this route with keycard rules."}}
        else:
            sample_route = route
            # Turn common dynamic Flask route syntax into a sample path so our guard can classify it.
            sample_route = sample_route.replace("<symbol>", "AAPL")
            sample_route = sample_route.replace("<string:symbol>", "AAPL")
            sample_route = sample_route.replace("<ticker>", "AAPL")
            sample_route = sample_route.replace("<position_id>", "sample_position")
            sample_route = sample_route.replace("<trade_id>", "sample_trade")
            sample_route = sample_route.replace("<path:filename>", "sample")
            sample_route = sample_route.replace("<filename>", "sample")

            match = match_ob_guard_policy(sample_route)
            match_type = match.get("match_type")

            if match_type == "public_safe":
                category = "public_safe"
            elif match_type == "exact":
                category = "guarded"
            elif match_type == "dynamic_symbol":
                category = "dynamic_guarded"
            elif match_type == "unmapped_default_deny":
                category = "unmapped_default_deny"
            else:
                category = "unmapped_default_deny"

        counts["total"] += 1
        counts[category] = counts.get(category, 0) + 1

        routes.append({
            "route": route,
            "endpoint": endpoint,
            "methods": methods,
            "category": category,
            "match_type": match.get("match_type"),
            "policy": match.get("policy"),
        })

    attention = [
        item for item in routes
        if item.get("category") == "unmapped_default_deny"
    ]

    return {
        "ok": True,
        "generated_at": _utc_now(),
        "tower_name": "The Tower",
        "counts": counts,
        "routes": routes,
        "attention": attention,
        "attention_count": len(attention),
        "default_deny_active": True,
        "human_reason": "OB route exposure report generated. Unmapped non-public routes are treated as default-deny until deliberately mapped.",
        "soulaana_translation": "Soulaana: I made the corridor map. Anything not named stays locked until you bless it.",
    }


def print_ob_route_exposure_report(app=None) -> Dict[str, Any]:
    import json
    report = build_ob_route_exposure_report(app=app)
    print("=" * 80)
    print("OB ROUTE EXPOSURE REPORT")
    print("=" * 80)
    print(json.dumps(report, indent=2, sort_keys=True, default=str))
    return report


if __name__ == "__main__":
    result = print_ob_route_exposure_report()
    if not result.get("ok"):
        raise SystemExit("OB route exposure report failed.")
