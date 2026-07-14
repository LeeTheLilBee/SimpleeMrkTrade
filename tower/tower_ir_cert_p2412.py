"""
SEARCHABLE LABEL: TOWER_PACK_2412_CONTRACT_VERSION_PIN

Pack 2412 — Contract Version Pin and Compatibility Gate
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_ir_cert_p2372 import CONTRACT_VERSION
from tower.tower_ir_cert_p2374 import (
    TRANSLATION_CONTRACT_VERSION,
)
from tower.tower_ir_cert_p2381 import (
    BRIDGE_REQUEST_VERSION,
)
from tower.tower_ir_cert_p2383 import (
    DECISION_ENVELOPE_VERSION,
)


PACK_ID = "2412"
ENDPOINT = "/tower/ir-cert-v2412.json"

CERTIFICATION_PROFILE_VERSION = (
    "tower-ob-protected-launch-certification-v1.0.0"
)

PINNED_VERSIONS = {
    "room_contract_version": CONTRACT_VERSION,
    "clearance_translation_version": (
        TRANSLATION_CONTRACT_VERSION
    ),
    "bridge_request_version": BRIDGE_REQUEST_VERSION,
    "decision_envelope_version": (
        DECISION_ENVELOPE_VERSION
    ),
    "certification_profile_version": (
        CERTIFICATION_PROFILE_VERSION
    ),
}


def evaluate_contract_compatibility(
    observed_versions: Dict[str, str],
) -> Dict[str, Any]:
    mismatches = []

    for name, required in PINNED_VERSIONS.items():
        observed = observed_versions.get(name)

        if observed != required:
            mismatches.append({
                "contract": name,
                "required_version": required,
                "observed_version": observed,
                "reason_code": (
                    "ob_contract_version_mismatch"
                ),
            })

    compatible = not mismatches

    return {
        "compatible": compatible,
        "reason_code": (
            "ob_contract_versions_compatible"
            if compatible
            else "ob_contract_version_mismatch"
        ),
        "pinned_versions": deepcopy(PINNED_VERSIONS),
        "mismatches": mismatches,
        "default_deny_on_mismatch": True,
        "preview_only": True,
        "writes_state": False,
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    compatibility = evaluate_contract_compatibility(
        deepcopy(PINNED_VERSIONS)
    )

    return {
        "pack": PACK_ID,
        "pack_name": (
            "Contract Version Pin and Compatibility Gate"
        ),
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "pinned_versions": deepcopy(PINNED_VERSIONS),
        "compatibility_check": compatibility,
        "default_deny_on_mismatch": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2413",
        "safe_to_continue_to_pack_2413": True,
    }


def build_ir_cert_p2412_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2413_ir_cert_p2413() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2413",
        "name": "Six-Room Certification Evidence Matrix",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
