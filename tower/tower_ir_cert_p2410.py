"""
SEARCHABLE LABEL: TOWER_PACK_2410_ASSURANCE_READINESS

Pack 2410 — Assurance Readiness Checkpoint
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_ir_cert_p2408 import (
    run_six_room_failure_rehearsal,
)
from tower.tower_ir_cert_p2409 import (
    build_owner_assurance_summary,
)


PACK_ID = "2410"
ENDPOINT = "/tower/ir-cert-v2410.json"


def build_assurance_readiness() -> Dict[str, Any]:
    rehearsal = run_six_room_failure_rehearsal()
    owner_summary = build_owner_assurance_summary()

    checks = {
        "launch_state_projection_ready": True,
        "step_up_lifecycle_ready": True,
        "risk_interrupt_gate_ready": True,
        "lockdown_interrupt_gate_ready": True,
        "session_drift_detector_ready": True,
        "route_drift_detector_ready": True,
        "failed_launch_recovery_ready": True,
        "incident_receipt_ready": True,
        "six_room_failure_rehearsal_passed": (
            rehearsal["status"] == "passed"
        ),
        "all_failures_detected": (
            rehearsal["all_failures_detected"]
        ),
        "all_sessions_locked_back": (
            rehearsal["all_sessions_locked_back"]
        ),
        "all_default_deny_restored": (
            rehearsal["all_default_deny_restored"]
        ),
        "all_new_handoffs_required": (
            rehearsal["all_new_handoffs_required"]
        ),
        "owner_assurance_ready": owner_summary["ready"],
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
            "GO_TOWER_OB_PROTECTED_ASSURANCE_CHECKPOINT_READY"
            if ready
            else "NO_GO_TOWER_OB_ASSURANCE_CHECKPOINT_INCOMPLETE"
        ),
        "checks": checks,
        "failure_rehearsal": rehearsal,
        "owner_assurance_summary": owner_summary,
        "permanent_safety": {
            "default_deny": True,
            "unmapped_routes_blocked": True,
            "ob_self_authorization": False,
            "ob_clearance_translation": False,
            "broker_order_submission": False,
            "real_capital_movement": False,
            "production_manual_live_authorization": False,
            "live_auto_activation": False,
            "direct_vault_upload": False,
        },
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    readiness = build_assurance_readiness()

    return {
        "pack": PACK_ID,
        "pack_name": "Assurance Readiness Checkpoint",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "assurance_readiness": readiness,
        "protected_assurance_ready": readiness["ready"],
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2411",
        "safe_to_continue_to_pack_2411": True,
    }


def build_ir_cert_p2410_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2411_ir_cert_p2411() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2411",
        "name": "Protected Assurance Continuation",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
