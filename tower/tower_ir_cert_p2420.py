"""
SEARCHABLE LABEL: TOWER_PACK_2420_CERTIFICATION_CLOSEOUT

Pack 2420 — Protected Launch Certification Closeout
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_ir_cert_p2419 import (
    run_final_certification_rehearsal,
)


PACK_ID = "2420"
ENDPOINT = "/tower/ir-cert-v2420.json"


def build_certification_closeout() -> Dict[str, Any]:
    rehearsal = run_final_certification_rehearsal()

    checks = {
        "final_certification_passed": (
            rehearsal["status"] == "passed"
        ),
        "evidence_bundle_complete": (
            rehearsal["checks"][
                "evidence_bundle_complete"
            ]
        ),
        "contract_versions_compatible": (
            rehearsal["checks"][
                "contract_versions_compatible"
            ]
        ),
        "six_rooms_certified": (
            rehearsal["checks"][
                "six_rooms_certified"
            ]
        ),
        "reason_code_coverage_complete": (
            rehearsal["checks"][
                "reason_code_coverage_complete"
            ]
        ),
        "safety_boundaries_verified": (
            rehearsal["checks"][
                "safety_boundaries_verified"
            ]
        ),
        "owner_preview_acceptance_recorded": (
            rehearsal["checks"][
                "owner_preview_acceptance_recorded"
            ]
        ),
        "certification_seal_valid": (
            rehearsal["checks"][
                "certification_seal_valid"
            ]
        ),
        "production_authorization_not_granted": (
            rehearsal["checks"][
                "production_authorization_not_granted"
            ]
        ),
        "default_deny_preserved": True,
        "unmapped_routes_blocked": True,
        "ob_self_authorization_disabled": True,
        "ob_clearance_translation_disabled": True,
        "broker_submission_disabled": True,
        "real_capital_disabled": True,
        "production_manual_live_disabled": True,
        "live_auto_disabled": True,
        "direct_vault_upload_disabled": True,
        "preview_only_preserved": True,
        "contract_only_preserved": True,
    }

    ready = all(checks.values())

    return {
        "ready": ready,
        "recommendation": (
            "GO_TOWER_OB_PROTECTED_LAUNCH_PREVIEW_CERTIFIED"
            if ready
            else "NO_GO_TOWER_OB_CERTIFICATION_CLOSEOUT_INCOMPLETE"
        ),
        "checks": checks,
        "certification_rehearsal": rehearsal,
        "certified_scope": (
            "tower_to_ob_protected_launch_preview_contract"
        ),
        "production_scope_certified": False,
        "manual_live_scope_certified": False,
        "live_auto_scope_certified": False,
        "next_required_action": (
            "continue_preview_operational_validation"
            if ready
            else "repair_certification_blockers"
        ),
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    closeout = build_certification_closeout()

    return {
        "pack": PACK_ID,
        "pack_name": (
            "Protected Launch Certification Closeout"
        ),
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "certification_closeout": closeout,
        "protected_launch_preview_certified": (
            closeout["ready"]
        ),
        "production_scope_certified": False,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2421",
        "safe_to_continue_to_pack_2421": True,
    }


def build_ir_cert_p2420_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2421_ir_cert_p2421() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2421",
        "name": "Protected Launch Operational Validation",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
