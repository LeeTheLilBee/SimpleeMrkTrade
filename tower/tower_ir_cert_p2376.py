"""
SEARCHABLE LABEL: TOWER_PACK_2376_PROTECTED_ROOM_MANIFEST

Pack 2376 — Protected Room Manifest

Returns only currently available rooms after Tower evaluation.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict, List

from tower.tower_ir_cert_p2372 import ROOMS
from tower.tower_ir_cert_p2375 import evaluate_room_access


PACK_ID = "2376"
ENDPOINT = "/tower/ir-cert-v2376.json"


def build_protected_room_manifest(
    *,
    tower_role: str,
    canonical_clearance_value: str,
    canonical_clearance_rank: int,
    identity_verified: bool,
    risk_state: str,
    lockdown_active: bool,
    mode: str,
    step_up_reference: str | None,
    step_up_valid: bool,
    object_context_by_room: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    available: List[Dict[str, Any]] = []
    denied: List[Dict[str, Any]] = []

    for room in ROOMS:
        decision = evaluate_room_access(
            room_id=room["room_id"],
            tower_role=tower_role,
            canonical_clearance_value=(
                canonical_clearance_value
            ),
            canonical_clearance_rank=(
                canonical_clearance_rank
            ),
            identity_verified=identity_verified,
            risk_state=risk_state,
            lockdown_active=lockdown_active,
            mode=mode,
            step_up_reference=step_up_reference,
            step_up_valid=step_up_valid,
            object_context=object_context_by_room.get(
                room["room_id"],
                {},
            ),
        )

        if decision["allowed"]:
            available.append({
                "room_id": room["room_id"],
                "display_name": room["display_name"],
                "canonical_route": (
                    room["canonical_route"]
                ),
                "launch_destination": (
                    room["launch_destination"]
                ),
                "required_clearance_value": (
                    room["required_clearance_value"]
                ),
                "required_clearance_rank": (
                    room["required_clearance_rank"]
                ),
                "step_up_required": (
                    room["step_up_required"]
                ),
                "allowed_modes": deepcopy(
                    room["allowed_modes"]
                ),
                "object_guard": deepcopy(
                    room["object_guard"]
                ),
                "reason_code": decision["reason_code"],
            })
        else:
            denied.append({
                "room_id": room["room_id"],
                "reason_code": decision["reason_code"],
            })

    return {
        "manifest_status": "ready",
        "available_room_count": len(available),
        "available_rooms": available,
        "denied_room_count": len(denied),
        "denied_rooms": denied,
        "default_deny": True,
        "authenticated_subject_required": True,
        "preview_only": True,
        "writes_state": False,
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    preview = build_protected_room_manifest(
        tower_role="owner",
        canonical_clearance_value="ob_owner_command",
        canonical_clearance_rank=900,
        identity_verified=True,
        risk_state="acceptable",
        lockdown_active=False,
        mode="paper",
        step_up_reference="stepup_preview",
        step_up_valid=True,
        object_context_by_room={
            "ob_room_symbol_page": {
                "symbol": "AMD",
            },
            "ob_room_trade_center": {
                "mission_account_id": "proof_demo",
            },
            "ob_room_review_center": {
                "mission_account_id": "proof_demo",
            },
            "ob_room_owner_console": {
                "mission_account_id": "proof_demo",
            },
        },
    )

    return {
        "pack": PACK_ID,
        "pack_name": "Protected Room Manifest",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "owner_preview_manifest": preview,
        "manifest_filters_before_return": True,
        "denied_rooms_not_exposed_as_launchable": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2377",
        "safe_to_continue_to_pack_2377": True,
    }


def build_ir_cert_p2376_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2377_ir_cert_p2377() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2377",
        "name": "Tower-to-OB Launch Handoff",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
