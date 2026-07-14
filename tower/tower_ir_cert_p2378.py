"""
SEARCHABLE LABEL: TOWER_PACK_2378_ROOM_ACCESS_RECEIPT

Pack 2378 — Room Access Receipt
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict


PACK_ID = "2378"
ENDPOINT = "/tower/ir-cert-v2378.json"


def _hash_payload(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def create_room_access_receipt(
    *,
    handoff: Dict[str, Any],
    bridge_decision: str,
    clearance_value: str,
    clearance_rank: int,
    step_up_state: str,
    launch_time: str,
) -> Dict[str, Any]:
    receipt_seed = {
        "handoff_id": handoff["handoff_id"],
        "room_id": handoff["approved_room_id"],
        "canonical_path": handoff["canonical_path"],
        "launch_time": launch_time,
    }

    receipt = {
        "receipt_id": (
            "obaccess_"
            + _hash_payload(receipt_seed)[:24]
        ),
        "handoff_id": handoff["handoff_id"],
        "owner_id": handoff["owner_id"],
        "session_id": handoff["session_id"],
        "bridge_decision": bridge_decision,
        "room_id": handoff["approved_room_id"],
        "canonical_route": handoff["canonical_path"],
        "clearance_value": clearance_value,
        "clearance_rank": clearance_rank,
        "step_up_reference": (
            handoff["step_up_reference"]
        ),
        "step_up_state": step_up_state,
        "launch_time": launch_time,
        "mode": handoff["mode"],
        "safety_locks": deepcopy(
            handoff["safety_boundaries"]
        ),
        "completion_state": "room_accessed_preview",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }

    receipt["integrity_hash"] = _hash_payload(receipt)

    return receipt


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": "Room Access Receipt",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "receipt_fields": [
            "receipt_id",
            "handoff_id",
            "bridge_decision",
            "room_id",
            "canonical_route",
            "clearance_value",
            "clearance_rank",
            "step_up_reference",
            "step_up_state",
            "launch_time",
            "mode",
            "safety_locks",
            "integrity_hash",
        ],
        "append_only_contract": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2379",
        "safe_to_continue_to_pack_2379": True,
    }


def build_ir_cert_p2378_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2379_ir_cert_p2379() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2379",
        "name": "Session Close and Lockback",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
