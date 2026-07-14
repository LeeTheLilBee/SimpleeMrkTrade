"""
SEARCHABLE LABEL: TOWER_PACK_2395_LAUNCH_USE_RECEIPT

Pack 2395 — Launch Use Receipt
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict


PACK_ID = "2395"
ENDPOINT = "/tower/ir-cert-v2395.json"


def _hash(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def create_launch_use_receipt(
    *,
    handoff: Dict[str, Any],
    enforcement_decision: Dict[str, Any],
    used_at: str,
    state_transition_reference: str,
) -> Dict[str, Any]:
    allowed = enforcement_decision.get("allowed") is True

    receipt = {
        "handoff_id": handoff["handoff_id"],
        "owner_id": handoff["owner_id"],
        "session_id": handoff["session_id"],
        "room_id": handoff["approved_room_id"],
        "canonical_path": handoff["canonical_path"],
        "mode": handoff["mode"],
        "used_at": used_at,
        "enforcement_decision": (
            "allow" if allowed else "deny"
        ),
        "reason_code": enforcement_decision.get(
            "reason_code"
        ),
        "state_transition_reference": (
            state_transition_reference
        ),
        "authorization_consumed": allowed,
        "replay_allowed": False,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }

    receipt["launch_use_receipt_id"] = (
        "obuse_" + _hash(receipt)[:24]
    )
    receipt["integrity_hash"] = _hash(receipt)

    return receipt


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": "Launch Use Receipt",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "authorization_consumed_on_allow": True,
        "replay_allowed": False,
        "single_room_use": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2396",
        "safe_to_continue_to_pack_2396": True,
    }


def build_ir_cert_p2395_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2396_ir_cert_p2396() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2396",
        "name": "Receipt Chain Integrity Contract",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
