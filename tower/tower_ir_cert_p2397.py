"""
SEARCHABLE LABEL: TOWER_PACK_2397_EMERGENCY_LOCKBACK

Pack 2397 — Abnormal Exit and Emergency Lockback
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict


PACK_ID = "2397"
ENDPOINT = "/tower/ir-cert-v2397.json"


def _hash(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def create_emergency_lockback(
    *,
    handoff: Dict[str, Any],
    trigger_code: str,
    detected_at: str,
) -> Dict[str, Any]:
    receipt = {
        "handoff_id": handoff["handoff_id"],
        "owner_id": handoff["owner_id"],
        "session_id": handoff["session_id"],
        "room_id": handoff["approved_room_id"],
        "trigger_code": trigger_code,
        "detected_at": detected_at,
        "launch_authorization_state": "revoked",
        "handoff_replay_state": "blocked",
        "step_up_state": (
            "revoked"
            if handoff.get("step_up_reference")
            else "not_required"
        ),
        "ob_access_state": "locked_back",
        "default_deny_restored": True,
        "unmapped_routes_blocked": True,
        "emergency_close": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }

    receipt["emergency_lockback_receipt_id"] = (
        "obemergency_" + _hash(receipt)[:24]
    )
    receipt["integrity_hash"] = _hash(receipt)

    return receipt


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": (
            "Abnormal Exit and Emergency Lockback"
        ),
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "supported_triggers": [
            "session_disconnect",
            "step_up_revoked",
            "risk_state_changed",
            "tower_lockdown_activated",
            "receipt_chain_failure",
            "owner_emergency_close",
        ],
        "default_deny_restored": True,
        "replay_blocked": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2398",
        "safe_to_continue_to_pack_2398": True,
    }


def build_ir_cert_p2397_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2398_ir_cert_p2398() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2398",
        "name": "Owner Session Audit Summary",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
