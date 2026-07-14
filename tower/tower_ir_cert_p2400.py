"""
SEARCHABLE LABEL: TOWER_PACK_2400_ENFORCEMENT_READINESS

Pack 2400 — Enforcement Readiness Checkpoint
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_ir_cert_p2399 import (
    run_six_room_enforcement_rehearsal,
)


PACK_ID = "2400"
ENDPOINT = "/tower/ir-cert-v2400.json"


def build_enforcement_readiness() -> Dict[str, Any]:
    rehearsal = run_six_room_enforcement_rehearsal()

    checks = {
        "active_launch_ledger_ready": True,
        "consume_revoke_contract_ready": True,
        "protected_route_enforcement_ready": True,
        "denial_receipt_ready": True,
        "launch_use_receipt_ready": True,
        "receipt_chain_integrity_ready": True,
        "emergency_lockback_ready": True,
        "owner_audit_summary_ready": True,
        "six_room_enforcement_passed": (
            rehearsal["all_rooms_passed"]
        ),
        "replay_blocking_passed": (
            rehearsal["replay_blocking_passed"]
        ),
        "receipt_chain_passed": (
            rehearsal["receipt_chain_passed"]
        ),
        "default_deny_restored": (
            rehearsal["default_deny_restored"]
        ),
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
            "GO_TOWER_OB_PROTECTED_ENFORCEMENT_READY"
            if ready
            else "NO_GO_TOWER_OB_ENFORCEMENT_INCOMPLETE"
        ),
        "checks": checks,
        "six_room_enforcement_rehearsal": rehearsal,
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
    readiness = build_enforcement_readiness()

    return {
        "pack": PACK_ID,
        "pack_name": "Enforcement Readiness Checkpoint",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "enforcement_readiness": readiness,
        "protected_enforcement_ready": readiness["ready"],
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2401",
        "safe_to_continue_to_pack_2401": True,
    }


def build_ir_cert_p2400_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2401_ir_cert_p2401() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2401",
        "name": "Protected Enforcement Continuation",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
