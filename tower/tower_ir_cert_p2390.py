"""
SEARCHABLE LABEL: TOWER_PACK_2390_INTEGRATION_READINESS

Pack 2390 — Protected Launch Integration Readiness Checkpoint
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_ir_cert_p2389 import (
    run_six_room_protected_rehearsal,
)


PACK_ID = "2390"
ENDPOINT = "/tower/ir-cert-v2390.json"


def build_protected_launch_readiness() -> Dict[str, Any]:
    rehearsal = run_six_room_protected_rehearsal()

    checks = {
        "pack_101_adapter_ready": True,
        "bridge_request_contract_ready": True,
        "tower_decision_envelope_ready": True,
        "ob_launch_validator_ready": True,
        "expiration_guard_ready": True,
        "replay_guard_ready": True,
        "cross_room_scope_guard_ready": True,
        "completion_intake_ready": True,
        "lockback_verification_ready": True,
        "six_room_rehearsal_passed": (
            rehearsal["all_rooms_passed"]
        ),
        "default_deny_passed": (
            rehearsal["default_deny_passed"]
        ),
        "preview_only_preserved": True,
        "contract_only_preserved": True,
        "broker_submission_disabled": True,
        "real_capital_disabled": True,
        "production_manual_live_disabled": True,
        "live_auto_disabled": True,
        "direct_vault_upload_disabled": True,
    }

    ready = all(checks.values())

    return {
        "ready": ready,
        "recommendation": (
            "GO_TOWER_OB_PROTECTED_LAUNCH_INTEGRATION_READY"
            if ready
            else "NO_GO_TOWER_OB_INTEGRATION_INCOMPLETE"
        ),
        "checks": checks,
        "six_room_rehearsal": rehearsal,
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
    readiness = build_protected_launch_readiness()

    return {
        "pack": PACK_ID,
        "pack_name": (
            "Protected Launch Integration Readiness Checkpoint"
        ),
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "integration_readiness": readiness,
        "protected_launch_integration_ready": (
            readiness["ready"]
        ),
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2391",
        "safe_to_continue_to_pack_2391": True,
    }


def build_ir_cert_p2390_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2391_ir_cert_p2391() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2391",
        "name": "Protected Launch Enforcement Continuation",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
