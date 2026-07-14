"""
SEARCHABLE LABEL: TOWER_PACK_2407_PROTECTED_LAUNCH_INCIDENT

Pack 2407 — Protected Launch Incident Receipt
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict


PACK_ID = "2407"
ENDPOINT = "/tower/ir-cert-v2407.json"


def _hash(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def create_protected_launch_incident_receipt(
    *,
    handoff: Dict[str, Any],
    incident_type: str,
    reason_code: str,
    incident_stage: str,
    detected_at: str,
    recovery_receipt: Dict[str, Any],
) -> Dict[str, Any]:
    receipt = {
        "handoff_id": handoff.get("handoff_id"),
        "owner_id": handoff.get("owner_id"),
        "session_id": handoff.get("session_id"),
        "room_id": handoff.get("approved_room_id"),
        "canonical_path": handoff.get("canonical_path"),
        "incident_type": incident_type,
        "reason_code": reason_code,
        "incident_stage": incident_stage,
        "detected_at": detected_at,
        "recovery_receipt_id": recovery_receipt.get(
            "recovery_receipt_id"
        ),
        "recovery_status": recovery_receipt.get(
            "recovery_status"
        ),
        "ob_access_state": recovery_receipt.get(
            "ob_access_state"
        ),
        "default_deny_restored": recovery_receipt.get(
            "default_deny_restored"
        ),
        "owner_safe": True,
        "raw_step_up_material_exposed": False,
        "raw_secret_material_exposed": False,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }

    receipt["incident_receipt_id"] = (
        "obincident_" + _hash(receipt)[:24]
    )
    receipt["integrity_hash"] = _hash(receipt)

    return receipt


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": "Protected Launch Incident Receipt",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "owner_safe": True,
        "raw_step_up_material_exposed": False,
        "raw_secret_material_exposed": False,
        "recovery_reference_required": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2408",
        "safe_to_continue_to_pack_2408": True,
    }


def build_ir_cert_p2407_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2408_ir_cert_p2408() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2408",
        "name": "Six-Room Failure Injection Rehearsal",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
