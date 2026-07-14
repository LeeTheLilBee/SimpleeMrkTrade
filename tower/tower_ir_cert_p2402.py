"""
SEARCHABLE LABEL: TOWER_PACK_2402_STEP_UP_LIFECYCLE

Pack 2402 — Step-Up Lifecycle Verification
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict


PACK_ID = "2402"
ENDPOINT = "/tower/ir-cert-v2402.json"


def verify_step_up_lifecycle(
    *,
    step_up_required: bool,
    step_up_reference: str | None,
    step_up_state: str,
    owner_id: str,
    step_up_owner_id: str | None,
    session_id: str,
    step_up_session_id: str | None,
    room_id: str,
    step_up_room_id: str | None,
) -> Dict[str, Any]:
    if not step_up_required:
        return {
            "allowed": True,
            "reason_code": "ob_step_up_not_required",
            "step_up_state": "not_required",
            "preview_only": True,
            "writes_state": False,
        }

    errors = []

    if not step_up_reference:
        errors.append("ob_step_up_required")

    if step_up_state != "validated":
        errors.append("ob_step_up_not_valid")

    if owner_id != step_up_owner_id:
        errors.append("ob_step_up_owner_mismatch")

    if session_id != step_up_session_id:
        errors.append("ob_step_up_session_mismatch")

    if room_id != step_up_room_id:
        errors.append("ob_step_up_room_scope_mismatch")

    allowed = not errors

    return {
        "allowed": allowed,
        "reason_code": (
            "ob_step_up_lifecycle_valid"
            if allowed
            else errors[0]
        ),
        "validation_errors": errors,
        "step_up_reference": step_up_reference,
        "step_up_state": step_up_state,
        "single_room_scope": True,
        "single_session_scope": True,
        "preview_only": True,
        "writes_state": False,
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": "Step-Up Lifecycle Verification",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "owner_match_required": True,
        "session_match_required": True,
        "room_match_required": True,
        "step_up_loss_blocks_access": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2403",
        "safe_to_continue_to_pack_2403": True,
    }


def build_ir_cert_p2402_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2403_ir_cert_p2403() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2403",
        "name": "Risk and Lockdown Interrupt Gate",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
