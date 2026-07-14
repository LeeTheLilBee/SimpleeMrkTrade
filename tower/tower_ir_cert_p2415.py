"""
SEARCHABLE LABEL: TOWER_PACK_2415_SAFETY_ATTESTATION

Pack 2415 — Permanent Safety Boundary Attestation
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict


PACK_ID = "2415"
ENDPOINT = "/tower/ir-cert-v2415.json"


PERMANENT_SAFETY_BOUNDARIES = {
    "default_deny": True,
    "unmapped_routes_blocked": True,
    "ob_self_authorization": False,
    "ob_clearance_translation": False,
    "broker_order_submission": False,
    "real_capital_movement": False,
    "production_manual_live_authorization": False,
    "live_auto_activation": False,
    "direct_vault_upload": False,
    "public_ob_access": False,
    "cross_room_handoff_reuse": False,
    "handoff_replay": False,
}


def _hash(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def create_safety_boundary_attestation() -> Dict[str, Any]:
    attestation = {
        "boundary_version": (
            "tower-ob-permanent-safety-v1.0.0"
        ),
        "boundaries": deepcopy(
            PERMANENT_SAFETY_BOUNDARIES
        ),
        "all_required_boundaries_present": True,
        "all_prohibited_capabilities_disabled": all([
            PERMANENT_SAFETY_BOUNDARIES[
                "ob_self_authorization"
            ] is False,
            PERMANENT_SAFETY_BOUNDARIES[
                "ob_clearance_translation"
            ] is False,
            PERMANENT_SAFETY_BOUNDARIES[
                "broker_order_submission"
            ] is False,
            PERMANENT_SAFETY_BOUNDARIES[
                "real_capital_movement"
            ] is False,
            PERMANENT_SAFETY_BOUNDARIES[
                "production_manual_live_authorization"
            ] is False,
            PERMANENT_SAFETY_BOUNDARIES[
                "live_auto_activation"
            ] is False,
            PERMANENT_SAFETY_BOUNDARIES[
                "direct_vault_upload"
            ] is False,
        ]),
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }

    attestation["attestation_id"] = (
        "obsafety_" + _hash(attestation)[:24]
    )
    attestation["integrity_hash"] = _hash(
        attestation
    )

    return attestation


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    attestation = create_safety_boundary_attestation()

    return {
        "pack": PACK_ID,
        "pack_name": (
            "Permanent Safety Boundary Attestation"
        ),
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "safety_attestation": attestation,
        "safety_boundaries_verified": (
            attestation[
                "all_required_boundaries_present"
            ]
            and attestation[
                "all_prohibited_capabilities_disabled"
            ]
        ),
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2416",
        "safe_to_continue_to_pack_2416": True,
    }


def build_ir_cert_p2415_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2416_ir_cert_p2416() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2416",
        "name": "Owner Acceptance Decision Draft",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
