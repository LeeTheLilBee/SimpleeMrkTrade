"""
SEARCHABLE LABEL: TOWER_PACK_2384_OB_LAUNCH_VALIDATOR

Pack 2384 — OB Launch Authorization Validator
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict


PACK_ID = "2384"
ENDPOINT = "/tower/ir-cert-v2384.json"


def _hash(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def validate_ob_launch_authorization(
    *,
    decision_envelope: Dict[str, Any],
    handoff: Dict[str, Any],
    owner_id: str,
    session_id: str,
    requested_path: str,
    requested_mode: str,
) -> Dict[str, Any]:
    expected_handoff_hash = handoff.get("integrity_hash")

    handoff_source = {
        key: value
        for key, value in handoff.items()
        if key != "integrity_hash"
    }

    errors = []

    if not decision_envelope.get("allowed"):
        errors.append(
            decision_envelope.get(
                "reason_code",
                "ob_launch_not_authorized",
            )
        )

    if not expected_handoff_hash:
        errors.append("ob_launch_integrity_hash_missing")

    elif _hash(handoff_source) != expected_handoff_hash:
        errors.append("ob_launch_integrity_hash_invalid")

    if handoff.get("owner_id") != owner_id:
        errors.append("ob_launch_owner_mismatch")

    if handoff.get("session_id") != session_id:
        errors.append("ob_launch_session_mismatch")

    if handoff.get("canonical_path") != requested_path:
        errors.append("ob_launch_path_scope_mismatch")

    if handoff.get("mode") != requested_mode:
        errors.append("ob_launch_mode_scope_mismatch")

    if (
        handoff.get("approved_room_id")
        != decision_envelope.get("room_id")
    ):
        errors.append("ob_launch_room_scope_mismatch")

    allowed = not errors

    return {
        "allowed": allowed,
        "reason_code": (
            "ob_launch_authorization_valid"
            if allowed
            else errors[0]
        ),
        "validation_errors": errors,
        "handoff_id": handoff.get("handoff_id"),
        "room_id": handoff.get("approved_room_id"),
        "canonical_path": handoff.get("canonical_path"),
        "mode": handoff.get("mode"),
        "authorization_scope": (
            "single_room_single_path_single_mode_single_session"
        ),
        "ob_self_authorization": False,
        "preview_only": True,
        "writes_state": False,
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": "OB Launch Authorization Validator",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "authorization_scope": (
            "single_room_single_path_single_mode_single_session"
        ),
        "owner_match_required": True,
        "session_match_required": True,
        "path_match_required": True,
        "mode_match_required": True,
        "integrity_hash_required": True,
        "ob_self_authorization": False,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2385",
        "safe_to_continue_to_pack_2385": True,
    }


def build_ir_cert_p2384_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2385_ir_cert_p2385() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2385",
        "name": "Handoff Expiration and Replay Guard",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
