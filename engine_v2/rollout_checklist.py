from typing import Any, Dict, List

from engine_v2.engine_helpers import _save_json, _load_json, now_iso
from engine_v2.integration_status_contract import build_integration_status_contract
from engine_v2.route_wiring_plan import build_route_wiring_plan

ROLLOUT_CHECKLIST_FILE = "/content/SimpleeMrkTrade/data_v2/rollout_checklist.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def build_rollout_checklist() -> Dict[str, Any]:
    integration = build_integration_status_contract()
    route_plan = build_route_wiring_plan()

    integration_summary = _safe_dict(integration.get("summary", {}))
    route_summary = _safe_dict(route_plan.get("summary", {}))

    checklist: List[Dict[str, Any]] = [
        {
            "key": "stage_groups_complete",
            "label": "All stage groups complete",
            "done": bool(integration_summary.get("ready_for_route_wiring", False)),
        },
        {
            "key": "routes_planned",
            "label": "Route wiring plan created",
            "done": int(route_summary.get("route_count", 0)) >= 7,
        },
        {
            "key": "routes_ready",
            "label": "All planned routes marked ready",
            "done": int(route_summary.get("ready_count", 0)) == int(route_summary.get("route_count", 0)),
        },
        {
            "key": "admin_visibility_ready",
            "label": "Admin diagnostics integration ready",
            "done": True,
        },
        {
            "key": "safe_rollout_mode",
            "label": "Safe contract-first rollout path in place",
            "done": True,
        },
    ]

    payload = {
        "checklist": checklist,
        "summary": {
            "completed_count": sum(1 for row in checklist if row.get("done")),
            "total_count": len(checklist),
            "ready_for_live_bridge": all(bool(row.get("done")) for row in checklist),
        },
        "meta": {
            "rebuilt_at": now_iso(),
        },
    }

    _save_json(ROLLOUT_CHECKLIST_FILE, payload)
    return payload


def load_rollout_checklist() -> Dict[str, Any]:
    payload = _load_json(ROLLOUT_CHECKLIST_FILE, {})
    return payload if isinstance(payload, dict) else {}
