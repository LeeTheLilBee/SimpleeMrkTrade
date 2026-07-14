"""
SEARCHABLE LABEL: TOWER_PACK_2379_SESSION_CLOSE_LOCKBACK

Pack 2379 — Session Close and Lockback
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict


PACK_ID = "2379"
ENDPOINT = "/tower/ir-cert-v2379.json"


def _hash_payload(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def close_ob_launch_session(
    *,
    handoff: Dict[str, Any],
    access_receipt: Dict[str, Any],
    close_time: str,
    close_reason: str,
) -> Dict[str, Any]:
    close_seed = {
        "handoff_id": handoff["handoff_id"],
        "access_receipt_id": access_receipt["receipt_id"],
        "close_time": close_time,
    }

    close_receipt = {
        "close_receipt_id": (
            "obclose_"
            + _hash_payload(close_seed)[:24]
        ),
        "handoff_id": handoff["handoff_id"],
        "access_receipt_id": (
            access_receipt["receipt_id"]
        ),
        "owner_id": handoff["owner_id"],
        "session_id": handoff["session_id"],
        "room_id": handoff["approved_room_id"],
        "close_time": close_time,
        "close_reason": close_reason,
        "launch_authorization_state": "revoked",
        "handoff_replay_state": "blocked",
        "step_up_state": (
            "consumed_or_revoked"
            if handoff["step_up_reference"]
            else "not_required"
        ),
        "ob_access_state": "locked_back",
        "default_deny_restored": True,
        "unmapped_routes_blocked": True,
        "completion_receipt_linked": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }

    close_receipt["integrity_hash"] = _hash_payload(
        close_receipt
    )

    return close_receipt


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": "Session Close and Lockback",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "close_sequence": [
            "validate_active_handoff",
            "link_completion_receipt",
            "revoke_launch_authorization",
            "consume_or_revoke_step_up",
            "block_handoff_replay",
            "restore_ob_default_deny",
            "create_close_receipt",
        ],
        "default_deny_restored": True,
        "replay_blocked_after_close": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2380",
        "safe_to_continue_to_pack_2380": True,
    }


def build_ir_cert_p2379_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2380_ir_cert_p2380() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2380",
        "name": "Owner Rehearsal Readiness Checkpoint",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
