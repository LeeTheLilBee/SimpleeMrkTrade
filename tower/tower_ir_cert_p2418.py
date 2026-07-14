"""
SEARCHABLE LABEL: TOWER_PACK_2418_CERTIFICATION_SEAL

Pack 2418 — Certification Seal and Integrity Contract
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict


PACK_ID = "2418"
ENDPOINT = "/tower/ir-cert-v2418.json"


def _hash(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def create_certification_seal(
    *,
    evidence_bundle: Dict[str, Any],
    contract_versions: Dict[str, str],
    certification_matrix: Dict[str, Any],
    safety_attestation: Dict[str, Any],
    owner_acceptance_receipt: Dict[str, Any],
) -> Dict[str, Any]:
    seal_source = {
        "evidence_bundle_id": evidence_bundle.get(
            "evidence_bundle_id"
        ),
        "evidence_integrity_hash": evidence_bundle.get(
            "integrity_hash"
        ),
        "contract_versions": deepcopy(
            contract_versions
        ),
        "all_six_rooms_certified": (
            certification_matrix.get(
                "all_rooms_certified"
            )
        ),
        "safety_attestation_id": safety_attestation.get(
            "attestation_id"
        ),
        "safety_integrity_hash": safety_attestation.get(
            "integrity_hash"
        ),
        "owner_acceptance_receipt_id": (
            owner_acceptance_receipt.get(
                "owner_acceptance_receipt_id"
            )
        ),
        "preview_contract_accepted": (
            owner_acceptance_receipt.get(
                "preview_contract_accepted"
            )
        ),
        "production_authorization_granted": False,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }

    seal_valid = all([
        bool(seal_source["evidence_bundle_id"]),
        bool(seal_source["evidence_integrity_hash"]),
        seal_source["all_six_rooms_certified"] is True,
        bool(seal_source["safety_attestation_id"]),
        bool(seal_source["safety_integrity_hash"]),
        seal_source["preview_contract_accepted"] is True,
        seal_source[
            "production_authorization_granted"
        ] is False,
    ])

    seal_source["seal_valid"] = seal_valid
    seal_source["certification_seal_id"] = (
        "obcertseal_" + _hash(seal_source)[:24]
    )
    seal_source["integrity_hash"] = _hash(
        seal_source
    )

    return seal_source


def verify_certification_seal(
    seal: Dict[str, Any],
) -> Dict[str, Any]:
    expected = seal.get("integrity_hash")

    source = {
        key: value
        for key, value in seal.items()
        if key != "integrity_hash"
    }

    valid = (
        bool(expected)
        and _hash(source) == expected
        and seal.get("seal_valid") is True
    )

    return {
        "valid": valid,
        "reason_code": (
            "tower_ob_certification_seal_valid"
            if valid
            else "tower_ob_certification_seal_invalid"
        ),
        "certification_seal_id": seal.get(
            "certification_seal_id"
        ),
        "preview_only": True,
        "writes_state": False,
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": (
            "Certification Seal and Integrity Contract"
        ),
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "seal_integrity_required": True,
        "owner_acceptance_required": True,
        "production_authorization_granted": False,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2419",
        "safe_to_continue_to_pack_2419": True,
    }


def build_ir_cert_p2418_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2419_ir_cert_p2419() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2419",
        "name": "Final Six-Room Certification Rehearsal",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
