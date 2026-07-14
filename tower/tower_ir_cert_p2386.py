"""
SEARCHABLE LABEL: TOWER_PACK_2386_CROSS_ROOM_SCOPE_GUARD

Pack 2386 — Cross-Room Session Scope Guard
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict


PACK_ID = "2386"
ENDPOINT = "/tower/ir-cert-v2386.json"


def evaluate_cross_room_scope(
    *,
    handoff: Dict[str, Any],
    requested_room_id: str,
    requested_path: str,
    requested_mode: str,
    requested_session_id: str,
) -> Dict[str, Any]:
    errors = []

    if handoff.get("approved_room_id") != requested_room_id:
        errors.append("ob_cross_room_launch_blocked")

    if handoff.get("canonical_path") != requested_path:
        errors.append("ob_launch_path_scope_mismatch")

    if handoff.get("mode") != requested_mode:
        errors.append("ob_launch_mode_scope_mismatch")

    if handoff.get("session_id") != requested_session_id:
        errors.append("ob_launch_session_mismatch")

    return {
        "allowed": not errors,
        "reason_code": (
            "ob_launch_scope_valid"
            if not errors
            else errors[0]
        ),
        "scope_errors": errors,
        "approved_room_id": handoff.get(
            "approved_room_id"
        ),
        "requested_room_id": requested_room_id,
        "cross_room_navigation_authorized": False,
        "new_handoff_required_for_room_change": True,
        "preview_only": True,
        "writes_state": False,
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": "Cross-Room Session Scope Guard",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "cross_room_navigation_authorized": False,
        "new_handoff_required_for_room_change": True,
        "same_session_not_sufficient_for_room_change": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2387",
        "safe_to_continue_to_pack_2387": True,
    }


def build_ir_cert_p2386_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2387_ir_cert_p2387() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2387",
        "name": "OB Completion Receipt Intake",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
