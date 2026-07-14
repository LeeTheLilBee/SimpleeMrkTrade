"""
SEARCHABLE LABEL: TOWER_PACK_2375_STEP_UP_ROOM_ACCESS_MATRIX

Pack 2375 — Step-Up Room Access Matrix
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_ir_cert_p2372 import get_room_by_id


PACK_ID = "2375"
ENDPOINT = "/tower/ir-cert-v2375.json"


def evaluate_room_access(
    *,
    room_id: str,
    tower_role: str,
    canonical_clearance_value: str,
    canonical_clearance_rank: int,
    identity_verified: bool,
    risk_state: str,
    lockdown_active: bool,
    mode: str,
    step_up_reference: str | None,
    step_up_valid: bool,
    object_context: Dict[str, Any] | None,
) -> Dict[str, Any]:
    room = get_room_by_id(room_id)

    base = {
        "room_id": room_id,
        "tower_role": tower_role,
        "canonical_clearance_value": (
            canonical_clearance_value
        ),
        "canonical_clearance_rank": (
            canonical_clearance_rank
        ),
        "mode": mode,
        "step_up_reference": step_up_reference,
        "preview_only": True,
        "writes_state": False,
    }

    if room is None:
        return {
            **base,
            "allowed": False,
            "reason_code": "ob_route_unmapped_default_deny",
        }

    role = str(tower_role or "").strip().lower()

    if not identity_verified:
        return {
            **base,
            "allowed": False,
            "reason_code": "ob_identity_missing",
        }

    if risk_state != "acceptable":
        return {
            **base,
            "allowed": False,
            "reason_code": "ob_risk_gate_denied",
        }

    if lockdown_active:
        return {
            **base,
            "allowed": False,
            "reason_code": "ob_lockdown_active",
        }

    if room["owner_only"] and role != "owner":
        return {
            **base,
            "allowed": False,
            "reason_code": "ob_owner_role_required",
        }

    if (
        not room["owner_only"]
        and role not in {
            "owner",
            "authorized_operator",
            "authorized_observer",
        }
    ):
        return {
            **base,
            "allowed": False,
            "reason_code": "ob_role_not_allowed",
        }

    if canonical_clearance_rank < room[
        "required_clearance_rank"
    ]:
        return {
            **base,
            "allowed": False,
            "reason_code": "ob_clearance_level_too_low",
            "required_clearance_value": room[
                "required_clearance_value"
            ],
            "required_clearance_rank": room[
                "required_clearance_rank"
            ],
        }

    if mode not in room["allowed_modes"]:
        return {
            **base,
            "allowed": False,
            "reason_code": "ob_mode_not_allowed",
            "allowed_modes": room["allowed_modes"],
        }

    if room["step_up_required"]:
        if not step_up_reference or not step_up_valid:
            return {
                **base,
                "allowed": False,
                "reason_code": "ob_step_up_required",
            }

    guard = room["object_guard"]
    context = object_context or {}

    if (
        guard["required"]
        and guard["object_id_required"]
        and not context.get(guard["object_id_field"])
    ):
        reason = (
            "ob_symbol_object_missing"
            if guard["object_type"] == "market_symbol"
            else "ob_mission_account_missing"
        )

        return {
            **base,
            "allowed": False,
            "reason_code": reason,
        }

    return {
        **base,
        "allowed": True,
        "reason_code": room["allow_reason_code"],
        "approved_room": deepcopy(room),
        "object_context": deepcopy(context),
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": "Step-Up Room Access Matrix",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "evaluation_order": [
            "room_registry",
            "identity",
            "risk",
            "lockdown",
            "role",
            "clearance",
            "mode",
            "step_up",
            "object_guard",
            "allow",
        ],
        "default_deny": True,
        "step_up_consumption_deferred_until_close": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2376",
        "safe_to_continue_to_pack_2376": True,
    }


def build_ir_cert_p2375_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2376_ir_cert_p2376() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2376",
        "name": "Protected Room Manifest",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
