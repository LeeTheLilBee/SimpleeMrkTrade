"""
SEARCHABLE LABEL: TOWER_PACK_2383_ROOM_DECISION_ENVELOPE

Pack 2383 — Tower Room Decision Envelope
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict


PACK_ID = "2383"
ENDPOINT = "/tower/ir-cert-v2383.json"

DECISION_ENVELOPE_VERSION = (
    "tower-ob-room-decision-v1.0.0"
)


def _hash(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def build_room_decision_envelope(
    *,
    bridge_request: Dict[str, Any],
    route_decision: Dict[str, Any],
    clearance_decision: Dict[str, Any],
    room_access_decision: Dict[str, Any],
) -> Dict[str, Any]:
    allowed = all([
        bridge_request.get("valid") is True,
        route_decision.get("allowed") is True,
        clearance_decision.get("allowed") is True,
        room_access_decision.get("allowed") is True,
    ])

    if not bridge_request.get("valid"):
        reason_code = bridge_request.get(
            "reason_code",
            "tower_ob_bridge_request_invalid",
        )
    elif not route_decision.get("allowed"):
        reason_code = route_decision.get(
            "reason_code",
            "ob_route_unmapped_default_deny",
        )
    elif not clearance_decision.get("allowed"):
        reason_code = clearance_decision.get(
            "reason_code",
            "ob_clearance_level_too_low",
        )
    else:
        reason_code = room_access_decision.get(
            "reason_code",
            "ob_room_contract_allow",
        )

    envelope = {
        "decision_envelope_version": (
            DECISION_ENVELOPE_VERSION
        ),
        "request_id": bridge_request.get("request_id"),
        "request_integrity_reference": bridge_request.get(
            "request_integrity_reference"
        ),
        "allowed": allowed,
        "reason_code": reason_code,
        "room_id": route_decision.get("room_id"),
        "canonical_path": route_decision.get(
            "canonical_path"
        ),
        "canonical_clearance_value": (
            clearance_decision.get(
                "canonical_clearance_value"
            )
        ),
        "canonical_clearance_rank": (
            clearance_decision.get(
                "canonical_clearance_rank",
                0,
            )
        ),
        "clearance_decision_reference": (
            clearance_decision.get(
                "clearance_decision_reference"
            )
        ),
        "step_up_reference": room_access_decision.get(
            "step_up_reference"
        ),
        "object_context": deepcopy(
            route_decision.get("object_context") or {}
        ),
        "default_deny": True,
        "ob_self_authorization": False,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }

    envelope["decision_integrity_hash"] = _hash(
        envelope
    )

    return envelope


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": "Tower Room Decision Envelope",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "decision_envelope_version": (
            DECISION_ENVELOPE_VERSION
        ),
        "integrity_hash_required": True,
        "single_authority": "tower",
        "ob_decision_override_enabled": False,
        "default_deny": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2384",
        "safe_to_continue_to_pack_2384": True,
    }


def build_ir_cert_p2383_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2384_ir_cert_p2384() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2384",
        "name": "OB Launch Authorization Validator",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
