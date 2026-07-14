"""
SEARCHABLE LABEL: TOWER_PACK_2419_FINAL_CERTIFICATION_REHEARSAL

Pack 2419 — Final Six-Room Certification Rehearsal
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_ir_cert_p2411 import (
    build_protected_launch_evidence_bundle,
)
from tower.tower_ir_cert_p2412 import (
    PINNED_VERSIONS,
    evaluate_contract_compatibility,
)
from tower.tower_ir_cert_p2413 import (
    build_six_room_certification_matrix,
)
from tower.tower_ir_cert_p2414 import (
    build_reason_code_coverage,
)
from tower.tower_ir_cert_p2415 import (
    create_safety_boundary_attestation,
)
from tower.tower_ir_cert_p2416 import (
    build_owner_acceptance_decision_draft,
)
from tower.tower_ir_cert_p2417 import (
    create_owner_acceptance_receipt,
)
from tower.tower_ir_cert_p2418 import (
    create_certification_seal,
    verify_certification_seal,
)


PACK_ID = "2419"
ENDPOINT = "/tower/ir-cert-v2419.json"


def run_final_certification_rehearsal() -> Dict[str, Any]:
    evidence = build_protected_launch_evidence_bundle()
    compatibility = evaluate_contract_compatibility(
        deepcopy(PINNED_VERSIONS)
    )
    matrix = build_six_room_certification_matrix()
    reason_coverage = build_reason_code_coverage()
    safety = create_safety_boundary_attestation()
    decision_draft = (
        build_owner_acceptance_decision_draft()
    )

    acceptance = create_owner_acceptance_receipt(
        owner_id="owner_rehearsal",
        decision_draft=decision_draft,
        owner_decision="accept_preview_contract",
        decided_at="2026-07-14T14:00:00+00:00",
    )

    seal = create_certification_seal(
        evidence_bundle=evidence,
        contract_versions=deepcopy(PINNED_VERSIONS),
        certification_matrix=matrix,
        safety_attestation=safety,
        owner_acceptance_receipt=acceptance,
    )

    seal_verification = verify_certification_seal(
        seal
    )

    checks = {
        "evidence_bundle_complete": all([
            evidence["integration_rehearsal_status"]
            == "passed",
            evidence["enforcement_rehearsal_status"]
            == "passed",
            evidence["failure_rehearsal_status"]
            == "passed",
        ]),
        "contract_versions_compatible": (
            compatibility["compatible"]
        ),
        "six_rooms_certified": (
            matrix["all_rooms_certified"]
        ),
        "reason_code_coverage_complete": (
            reason_coverage["coverage_complete"]
        ),
        "safety_boundaries_verified": all([
            safety["all_required_boundaries_present"],
            safety[
                "all_prohibited_capabilities_disabled"
            ],
        ]),
        "owner_decision_draft_acceptable": (
            decision_draft["acceptable"]
        ),
        "owner_preview_acceptance_recorded": (
            acceptance["preview_contract_accepted"]
        ),
        "certification_seal_valid": (
            seal_verification["valid"]
        ),
        "production_authorization_not_granted": (
            acceptance[
                "production_authorization_granted"
            ] is False
            and seal[
                "production_authorization_granted"
            ] is False
        ),
    }

    passed = all(checks.values())

    return {
        "status": "passed" if passed else "failed",
        "recommendation": (
            "GO_TOWER_OB_PREVIEW_CONTRACT_CERTIFIED"
            if passed
            else "NO_GO_TOWER_OB_CERTIFICATION_INCOMPLETE"
        ),
        "checks": checks,
        "evidence_bundle": evidence,
        "compatibility": compatibility,
        "certification_matrix": matrix,
        "reason_code_coverage": reason_coverage,
        "safety_attestation": safety,
        "owner_decision_draft": decision_draft,
        "owner_acceptance_receipt": acceptance,
        "certification_seal": seal,
        "seal_verification": seal_verification,
        "production_authorization_granted": False,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    rehearsal = run_final_certification_rehearsal()

    return {
        "pack": PACK_ID,
        "pack_name": (
            "Final Six-Room Certification Rehearsal"
        ),
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "certification_rehearsal": rehearsal,
        "final_certification_passed": (
            rehearsal["status"] == "passed"
        ),
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2420",
        "safe_to_continue_to_pack_2420": True,
    }


def build_ir_cert_p2419_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2420_ir_cert_p2420() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2420",
        "name": "Protected Launch Certification Closeout",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
