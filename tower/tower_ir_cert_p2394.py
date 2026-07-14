"""
SEARCHABLE LABEL: TOWER_PACK_2394_AUTHORIZATION_DENIAL_RECEIPT

Pack 2394 — Authorization Denial Receipt
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict


PACK_ID = "2394"
ENDPOINT = "/tower/ir-cert-v2394.json"


def _hash(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def create_authorization_denial_receipt(
    *,
    request_id: str,
    owner_id: str,
    session_id: str,
    requested_room_id: str | None,
    requested_path: str,
    requested_mode: str,
    reason_code: str,
    denied_at: str,
    handoff_id: str | None,
) -> Dict[str, Any]:
    receipt = {
        "request_id": request_id,
        "owner_id": owner_id,
        "session_id": session_id,
        "handoff_id": handoff_id,
        "requested_room_id": requested_room_id,
        "requested_path": requested_path,
        "requested_mode": requested_mode,
        "decision": "deny",
        "reason_code": reason_code,
        "denied_at": denied_at,
        "default_deny_preserved": True,
        "ob_access_granted": False,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }

    receipt["denial_receipt_id"] = (
        "obdeny_" + _hash(receipt)[:24]
    )
    receipt["integrity_hash"] = _hash(receipt)

    return receipt


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": "Authorization Denial Receipt",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "receipt_required_for_denial": True,
        "default_deny_preserved": True,
        "denial_does_not_disclose_hidden_rooms": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2395",
        "safe_to_continue_to_pack_2395": True,
    }


def build_ir_cert_p2394_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2395_ir_cert_p2395() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2395",
        "name": "Launch Use Receipt",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
