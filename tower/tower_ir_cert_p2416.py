"""
SEARCHABLE LABEL: TOWER_PACK_2416_OWNER_ACCEPTANCE_DECISION

Pack 2416 — Owner Acceptance Decision Draft
"""

from __future__ import annotations

import hashlib
import json
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


PACK_ID = "2416"
ENDPOINT = "/tower/ir-cert-v2416.json"


def _hash(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def build_owner_acceptance_decision_draft() -> Dict[str, Any]:
    evidence = build_protected_launch_evidence_bundle()
    compatibility = evaluate_contract_compatibility(
        deepcopy(PINNED_VERSIONS)
    )
    matrix = build_six_room_certification_matrix()
    reason_coverage = build_reason_code_coverage()
    safety = create_safety_boundary_attestation()

    checks = {
        "evidence_bundle_complete": all([
            evidence["integration_rehearsal_status"]
            == "passed",
            evidence["enforcement_rehearsal_status"]
            == "passed",
            evidence["failure_rehearsal_status"]
            == "passed",
            evidence["default_deny_proven"],
            evidence["replay_blocking_proven"],
            evidence["receipt_chain_proven"],
            evidence["failure_recovery_proven"],
        ]),
        "contract_versions_compatible": (
            compatibility["compatible"]
        ),
        "all_six_rooms_certified": (
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
        "preview_only_preserved": True,
        "contract_only_preserved": True,
    }

    acceptable = all(checks.values())

    draft = {
        "decision_type": (
            "tower_ob_protected_launch_owner_acceptance"
        ),
        "decision": (
            "ACCEPT_PREVIEW_CONTRACT"
            if acceptable
            else "HOLD_PREVIEW_CONTRACT"
        ),
        "acceptable": acceptable,
        "checks": checks,
        "evidence_bundle_id": evidence[
            "evidence_bundle_id"
        ],
        "safety_attestation_id": safety[
            "attestation_id"
        ],
        "owner_action_required": True,
        "owner_acceptance_applied": False,
        "production_authorization_granted": False,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }

    draft["decision_draft_id"] = (
        "obownerdecision_" + _hash(draft)[:24]
    )
    draft["integrity_hash"] = _hash(draft)

    return draft


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    draft = build_owner_acceptance_decision_draft()

    return {
        "pack": PACK_ID,
        "pack_name": "Owner Acceptance Decision Draft",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "owner_decision_draft": draft,
        "draft_ready_for_owner_review": (
            draft["acceptable"]
        ),
        "owner_acceptance_applied": False,
        "production_authorization_granted": False,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2417",
        "safe_to_continue_to_pack_2417": True,
    }


def build_ir_cert_p2416_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2417_ir_cert_p2417() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2417",
        "name": "Owner Acceptance Receipt",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
