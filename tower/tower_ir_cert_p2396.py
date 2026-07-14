"""
SEARCHABLE LABEL: TOWER_PACK_2396_RECEIPT_CHAIN_INTEGRITY

Pack 2396 — Receipt Chain Integrity Contract
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict


PACK_ID = "2396"
ENDPOINT = "/tower/ir-cert-v2396.json"


def verify_launch_receipt_chain(
    *,
    handoff: Dict[str, Any],
    launch_use_receipt: Dict[str, Any],
    room_access_receipt: Dict[str, Any],
    completion_intake: Dict[str, Any],
    close_receipt: Dict[str, Any],
) -> Dict[str, Any]:
    handoff_id = handoff["handoff_id"]

    checks = {
        "launch_use_handoff_match": (
            launch_use_receipt.get("handoff_id")
            == handoff_id
        ),
        "access_handoff_match": (
            room_access_receipt.get("handoff_id")
            == handoff_id
        ),
        "completion_handoff_match": (
            completion_intake.get("handoff_id")
            == handoff_id
        ),
        "close_handoff_match": (
            close_receipt.get("handoff_id")
            == handoff_id
        ),
        "owner_match": (
            launch_use_receipt.get("owner_id")
            == handoff.get("owner_id")
        ),
        "session_match": (
            launch_use_receipt.get("session_id")
            == handoff.get("session_id")
        ),
        "room_match": (
            launch_use_receipt.get("room_id")
            == handoff.get("approved_room_id")
        ),
        "path_match": (
            launch_use_receipt.get("canonical_path")
            == handoff.get("canonical_path")
        ),
        "authorization_consumed": (
            launch_use_receipt.get(
                "authorization_consumed"
            ) is True
        ),
        "completion_accepted": (
            completion_intake.get("accepted") is True
        ),
        "close_revoked": (
            close_receipt.get(
                "launch_authorization_state"
            ) == "revoked"
        ),
        "lockback_complete": (
            close_receipt.get("ob_access_state")
            == "locked_back"
        ),
    }

    verified = all(checks.values())

    return {
        "verified": verified,
        "reason_code": (
            "tower_ob_receipt_chain_verified"
            if verified
            else "tower_ob_receipt_chain_broken"
        ),
        "handoff_id": handoff_id,
        "checks": checks,
        "chain_order": [
            "launch_handoff",
            "launch_use_receipt",
            "room_access_receipt",
            "completion_intake",
            "close_receipt",
        ],
        "preview_only": True,
        "writes_state": False,
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": "Receipt Chain Integrity Contract",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "required_chain_order": [
            "launch_handoff",
            "launch_use_receipt",
            "room_access_receipt",
            "completion_intake",
            "close_receipt",
        ],
        "broken_chain_default_deny": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2397",
        "safe_to_continue_to_pack_2397": True,
    }


def build_ir_cert_p2396_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2397_ir_cert_p2397() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2397",
        "name": "Abnormal Exit and Emergency Lockback",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
