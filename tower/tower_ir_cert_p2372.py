"""
SEARCHABLE LABEL: TOWER_PACK_2372_OBSERVATORY_ROOM_REGISTRY

Tower — Observatory Protected Room Access and Launch Contract

Pack 2372 — Observatory Room Registry
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict, List


PACK_ID = "2372"
ENDPOINT = "/tower/ir-cert-v2372.json"

APP_ID = "the_observatory"
APP_ALIASES = (
    "observatory",
    "the-observatory",
    "ob",
    "simpleemrktrade",
)

REQUEST_TYPE = "tower.observatory.protected_room.launch"
REQUEST_TYPE_ALIASES = (
    "tower.ob.protected_room.launch",
    "observatory.protected_room.launch",
    "ob.protected_room.launch",
)

CONTRACT_VERSION = "tower-ob-access-v1.0.0"

DEFAULT_DENY_REASON = "ob_route_unmapped_default_deny"
ALLOW_REASON = "ob_room_contract_allow"

CANONICAL_CLEARANCES = {
    "ob_protected_read": {
        "value": "ob_protected_read",
        "rank": 300,
    },
    "ob_protected_workflow": {
        "value": "ob_protected_workflow",
        "rank": 500,
    },
    "ob_owner_command": {
        "value": "ob_owner_command",
        "rank": 900,
    },
}

ROOMS: List[Dict[str, Any]] = [
    {
        "room_id": "ob_room_dashboard",
        "display_name": "Dashboard",
        "canonical_route": "/dashboard",
        "accepted_aliases": [
            "/ob/dashboard",
            "/observatory/dashboard",
        ],
        "required_role": "owner_or_authorized_operator",
        "required_clearance_value": "ob_protected_read",
        "required_clearance_rank": 300,
        "step_up_required": False,
        "allowed_modes": [
            "survey",
            "paper",
            "manual_live_preview",
        ],
        "owner_only": False,
        "object_guard": {
            "required": False,
            "object_type": None,
            "object_id_required": False,
        },
        "lockdown_state": "tower_guarded_default_deny",
        "launch_destination": "/dashboard",
        "allow_reason_code": "ob_room_contract_allow",
        "deny_reason_codes": [
            "ob_identity_missing",
            "ob_role_not_allowed",
            "ob_clearance_level_too_low",
            "ob_mode_not_allowed",
            "ob_lockdown_active",
            "ob_risk_gate_denied",
        ],
    },
    {
        "room_id": "ob_room_market_map",
        "display_name": "Market Map",
        "canonical_route": "/market-map",
        "accepted_aliases": [
            "/ob/market-map",
            "/market-map-v10",
            "/observatory/market-map",
        ],
        "required_role": "owner_or_authorized_operator",
        "required_clearance_value": "ob_protected_read",
        "required_clearance_rank": 300,
        "step_up_required": False,
        "allowed_modes": [
            "survey",
            "paper",
            "manual_live_preview",
        ],
        "owner_only": False,
        "object_guard": {
            "required": False,
            "object_type": None,
            "object_id_required": False,
        },
        "lockdown_state": "tower_guarded_default_deny",
        "launch_destination": "/market-map",
        "allow_reason_code": "ob_room_contract_allow",
        "deny_reason_codes": [
            "ob_identity_missing",
            "ob_role_not_allowed",
            "ob_clearance_level_too_low",
            "ob_mode_not_allowed",
            "ob_lockdown_active",
            "ob_risk_gate_denied",
        ],
    },
    {
        "room_id": "ob_room_symbol_page",
        "display_name": "Symbol Page",
        "canonical_route": "/symbol/<symbol>",
        "accepted_aliases": [
            "/ob/symbol/<symbol>",
            "/symbol-page-v10/<symbol>",
            "/observatory/symbol/<symbol>",
        ],
        "required_role": "owner_or_authorized_operator",
        "required_clearance_value": "ob_protected_read",
        "required_clearance_rank": 300,
        "step_up_required": False,
        "allowed_modes": [
            "survey",
            "paper",
            "manual_live_preview",
        ],
        "owner_only": False,
        "object_guard": {
            "required": True,
            "object_type": "market_symbol",
            "object_id_required": True,
            "object_id_field": "symbol",
            "validation": "uppercase_listed_symbol",
        },
        "lockdown_state": "tower_guarded_default_deny",
        "launch_destination": "/symbol/{symbol}",
        "allow_reason_code": "ob_room_contract_allow",
        "deny_reason_codes": [
            "ob_identity_missing",
            "ob_role_not_allowed",
            "ob_clearance_level_too_low",
            "ob_symbol_object_missing",
            "ob_symbol_object_invalid",
            "ob_mode_not_allowed",
            "ob_lockdown_active",
            "ob_risk_gate_denied",
        ],
    },
    {
        "room_id": "ob_room_trade_center",
        "display_name": "Trade Center",
        "canonical_route": "/trade-center",
        "accepted_aliases": [
            "/ob/trade-center",
            "/observatory/trade-center",
        ],
        "required_role": "owner_or_authorized_operator",
        "required_clearance_value": "ob_protected_workflow",
        "required_clearance_rank": 500,
        "step_up_required": True,
        "allowed_modes": [
            "paper",
            "manual_live_preview",
        ],
        "owner_only": False,
        "object_guard": {
            "required": True,
            "object_type": "mission_account",
            "object_id_required": True,
            "object_id_field": "mission_account_id",
        },
        "lockdown_state": "tower_guarded_default_deny",
        "launch_destination": "/trade-center",
        "allow_reason_code": "ob_room_contract_allow",
        "deny_reason_codes": [
            "ob_identity_missing",
            "ob_role_not_allowed",
            "ob_clearance_level_too_low",
            "ob_step_up_required",
            "ob_mission_account_missing",
            "ob_mode_not_allowed",
            "ob_lockdown_active",
            "ob_risk_gate_denied",
        ],
    },
    {
        "room_id": "ob_room_review_center",
        "display_name": "Review Center",
        "canonical_route": "/review-center",
        "accepted_aliases": [
            "/ob/review-center",
            "/observatory/review-center",
        ],
        "required_role": "owner_or_authorized_operator",
        "required_clearance_value": "ob_protected_workflow",
        "required_clearance_rank": 500,
        "step_up_required": True,
        "allowed_modes": [
            "paper",
            "manual_live_preview",
        ],
        "owner_only": False,
        "object_guard": {
            "required": True,
            "object_type": "mission_account",
            "object_id_required": True,
            "object_id_field": "mission_account_id",
        },
        "lockdown_state": "tower_guarded_default_deny",
        "launch_destination": "/review-center",
        "allow_reason_code": "ob_room_contract_allow",
        "deny_reason_codes": [
            "ob_identity_missing",
            "ob_role_not_allowed",
            "ob_clearance_level_too_low",
            "ob_step_up_required",
            "ob_mission_account_missing",
            "ob_mode_not_allowed",
            "ob_lockdown_active",
            "ob_risk_gate_denied",
        ],
    },
    {
        "room_id": "ob_room_owner_console",
        "display_name": "Owner Console",
        "canonical_route": "/owner-console",
        "accepted_aliases": [
            "/ob/owner-console",
            "/observatory/owner-console",
        ],
        "required_role": "owner",
        "required_clearance_value": "ob_owner_command",
        "required_clearance_rank": 900,
        "step_up_required": True,
        "allowed_modes": [
            "survey",
            "paper",
            "manual_live_preview",
        ],
        "owner_only": True,
        "object_guard": {
            "required": True,
            "object_type": "owner_mission_scope",
            "object_id_required": True,
            "object_id_field": "mission_account_id",
        },
        "lockdown_state": "tower_guarded_default_deny",
        "launch_destination": "/owner-console",
        "allow_reason_code": "ob_room_contract_allow",
        "deny_reason_codes": [
            "ob_identity_missing",
            "ob_owner_role_required",
            "ob_clearance_level_too_low",
            "ob_step_up_required",
            "ob_mission_account_missing",
            "ob_mode_not_allowed",
            "ob_lockdown_active",
            "ob_risk_gate_denied",
        ],
    },
]


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": "Observatory Room Registry",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "app_id": APP_ID,
        "accepted_app_aliases": list(APP_ALIASES),
        "supported_request_type": REQUEST_TYPE,
        "accepted_request_type_aliases": list(
            REQUEST_TYPE_ALIASES
        ),
        "contract_version": CONTRACT_VERSION,
        "room_count": len(ROOMS),
        "rooms": deepcopy(ROOMS),
        "canonical_clearances": deepcopy(
            CANONICAL_CLEARANCES
        ),
        "default_deny": True,
        "unmapped_routes_blocked": True,
        "ob_self_authorization_enabled": False,
        "ob_clearance_translation_enabled": False,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2373",
        "safe_to_continue_to_pack_2373": True,
    }


def build_ir_cert_p2372_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def get_observatory_room_registry() -> Dict[str, Any]:
    payload = _build_cached()

    return {
        "app_id": payload["app_id"],
        "contract_version": payload["contract_version"],
        "supported_request_type": (
            payload["supported_request_type"]
        ),
        "rooms": deepcopy(payload["rooms"]),
    }


def get_room_by_id(room_id: str) -> Dict[str, Any] | None:
    for room in ROOMS:
        if room["room_id"] == room_id:
            return deepcopy(room)

    return None


def prepare_pack_2373_ir_cert_p2373() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2373",
        "name": "Canonical Route and Alias Contract",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
