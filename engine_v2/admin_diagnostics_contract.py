from typing import Any, Dict, List

from engine_v2.engine_helpers import _save_json, _load_json, now_iso
from engine_v2.integration_status_contract import build_integration_status_contract
from engine_v2.route_wiring_plan import build_route_wiring_plan

ADMIN_DIAGNOSTICS_FILE = "/content/SimpleeMrkTrade/data_v2/admin_diagnostics_contract.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def build_admin_diagnostics_contract() -> Dict[str, Any]:
    integration = build_integration_status_contract()
    route_plan = build_route_wiring_plan()

    checks = _safe_dict(integration.get("checks", {}))
    routes = _safe_list(route_plan.get("routes", []))

    status_cards = [
        {
            "key": key,
            "label": key.replace("_", " ").title(),
            "ok": bool(value),
        }
        for key, value in checks.items()
    ]

    route_cards = [
        {
            "route": row.get("route"),
            "status": row.get("status"),
            "target_contract": row.get("target_contract"),
        }
        for row in routes if isinstance(row, dict)
    ]

    payload = {
        "status_cards": status_cards,
        "route_cards": route_cards,
        "summary": {
            "all_groups_ready": all(bool(v) for v in checks.values()) if checks else False,
            "route_ready_count": sum(1 for row in route_cards if row.get("status") == "ready"),
            "status_group_count": len(status_cards),
        },
        "meta": {
            "rebuilt_at": now_iso(),
        },
    }

    _save_json(ADMIN_DIAGNOSTICS_FILE, payload)
    return payload


def load_admin_diagnostics_contract() -> Dict[str, Any]:
    payload = _load_json(ADMIN_DIAGNOSTICS_FILE, {})
    return payload if isinstance(payload, dict) else {}
