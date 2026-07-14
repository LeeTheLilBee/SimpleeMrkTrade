"""
SEARCHABLE LABEL: TOWER_PACK_2387_OB_COMPLETION_RECEIPT_INTAKE

Pack 2387 — OB Completion Receipt Intake
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict


PACK_ID = "2387"
ENDPOINT = "/tower/ir-cert-v2387.json"


def _hash(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def intake_ob_completion_receipt(
    *,
    handoff: Dict[str, Any],
    ob_completion_payload: Dict[str, Any],
) -> Dict[str, Any]:
    errors = []

    if (
        ob_completion_payload.get("handoff_id")
        != handoff.get("handoff_id")
    ):
        errors.append("ob_completion_handoff_mismatch")

    if (
        ob_completion_payload.get("session_id")
        != handoff.get("session_id")
    ):
        errors.append("ob_completion_session_mismatch")

    if (
        ob_completion_payload.get("room_id")
        != handoff.get("approved_room_id")
    ):
        errors.append("ob_completion_room_mismatch")

    if (
        ob_completion_payload.get("canonical_path")
        != handoff.get("canonical_path")
    ):
        errors.append("ob_completion_path_mismatch")

    allowed_states = {
        "completed_preview",
        "exited_preview",
        "cancelled_preview",
    }

    if (
        ob_completion_payload.get("completion_state")
        not in allowed_states
    ):
        errors.append("ob_completion_state_invalid")

    accepted = not errors

    receipt = {
        "accepted": accepted,
        "reason_code": (
            "tower_ob_completion_receipt_accepted"
            if accepted
            else errors[0]
        ),
        "validation_errors": errors,
        "handoff_id": handoff.get("handoff_id"),
        "session_id": handoff.get("session_id"),
        "room_id": handoff.get("approved_room_id"),
        "canonical_path": handoff.get("canonical_path"),
        "completion_state": ob_completion_payload.get(
            "completion_state"
        ),
        "completion_time": ob_completion_payload.get(
            "completion_time"
        ),
        "ob_receipt_reference": ob_completion_payload.get(
            "ob_receipt_reference"
        ),
        "append_only_contract": True,
        "preview_only": True,
        "writes_state": False,
    }

    receipt["tower_intake_integrity_hash"] = _hash(
        receipt
    )

    return receipt


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": "OB Completion Receipt Intake",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "handoff_match_required": True,
        "session_match_required": True,
        "room_match_required": True,
        "path_match_required": True,
        "append_only_contract": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2388",
        "safe_to_continue_to_pack_2388": True,
    }


def build_ir_cert_p2387_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2388_ir_cert_p2388() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2388",
        "name": "Lockback Verification Contract",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
