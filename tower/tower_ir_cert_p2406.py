"""
SEARCHABLE LABEL: TOWER_PACK_2406_FAILED_LAUNCH_RECOVERY

Pack 2406 — Failed Launch Recovery and Lockback
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict


PACK_ID = "2406"
ENDPOINT = "/tower/ir-cert-v2406.json"


def _hash(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def recover_failed_protected_launch(
    *,
    handoff: Dict[str, Any],
    failure_code: str,
    failure_stage: str,
    detected_at: str,
    step_up_required: bool,
) -> Dict[str, Any]:
    recovery = {
        "handoff_id": handoff.get("handoff_id"),
        "owner_id": handoff.get("owner_id"),
        "session_id": handoff.get("session_id"),
        "room_id": handoff.get("approved_room_id"),
        "failure_code": failure_code,
        "failure_stage": failure_stage,
        "detected_at": detected_at,
        "launch_authorization_state": "revoked",
        "handoff_replay_state": "blocked",
        "step_up_state": (
            "revoked"
            if step_up_required
            else "not_required"
        ),
        "ob_access_state": "locked_back",
        "default_deny_restored": True,
        "unmapped_routes_blocked": True,
        "new_handoff_required": True,
        "recovery_status": "recovered_preview",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }

    recovery["recovery_receipt_id"] = (
        "obrecovery_" + _hash(recovery)[:24]
    )
    recovery["integrity_hash"] = _hash(recovery)

    return recovery


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": "Failed Launch Recovery and Lockback",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "supported_failure_stages": [
            "bridge_request",
            "clearance_translation",
            "step_up",
            "manifest",
            "handoff",
            "route_enforcement",
            "ob_room_entry",
            "completion_receipt",
            "session_close",
        ],
        "authorization_revoked_on_failure": True,
        "default_deny_restored": True,
        "new_handoff_required": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2407",
        "safe_to_continue_to_pack_2407": True,
    }


def build_ir_cert_p2406_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2407_ir_cert_p2407() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2407",
        "name": "Protected Launch Incident Receipt",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
