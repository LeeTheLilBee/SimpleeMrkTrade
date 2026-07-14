"""
SEARCHABLE LABEL: TOWER_PACK_2388_LOCKBACK_VERIFICATION

Pack 2388 — Lockback Verification Contract
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict


PACK_ID = "2388"
ENDPOINT = "/tower/ir-cert-v2388.json"


def verify_ob_lockback(
    *,
    handoff: Dict[str, Any],
    completion_intake: Dict[str, Any],
    close_receipt: Dict[str, Any],
) -> Dict[str, Any]:
    checks = {
        "completion_receipt_accepted": (
            completion_intake.get("accepted") is True
        ),
        "handoff_ids_match": (
            close_receipt.get("handoff_id")
            == handoff.get("handoff_id")
        ),
        "launch_authorization_revoked": (
            close_receipt.get(
                "launch_authorization_state"
            ) == "revoked"
        ),
        "replay_blocked": (
            close_receipt.get("handoff_replay_state")
            == "blocked"
        ),
        "ob_locked_back": (
            close_receipt.get("ob_access_state")
            == "locked_back"
        ),
        "default_deny_restored": (
            close_receipt.get("default_deny_restored")
            is True
        ),
        "unmapped_routes_blocked": (
            close_receipt.get("unmapped_routes_blocked")
            is True
        ),
        "step_up_closed": (
            close_receipt.get("step_up_state")
            in {
                "consumed_or_revoked",
                "not_required",
            }
        ),
    }

    verified = all(checks.values())

    return {
        "verified": verified,
        "reason_code": (
            "tower_ob_lockback_verified"
            if verified
            else "tower_ob_lockback_incomplete"
        ),
        "checks": checks,
        "handoff_id": handoff.get("handoff_id"),
        "room_id": handoff.get("approved_room_id"),
        "default_deny_active": verified,
        "ob_access_state": (
            "locked_back"
            if verified
            else "lockback_unverified"
        ),
        "preview_only": True,
        "writes_state": False,
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": "Lockback Verification Contract",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "required_checks": [
            "completion_receipt_accepted",
            "handoff_ids_match",
            "launch_authorization_revoked",
            "replay_blocked",
            "ob_locked_back",
            "default_deny_restored",
            "unmapped_routes_blocked",
            "step_up_closed",
        ],
        "default_deny_required_after_close": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2389",
        "safe_to_continue_to_pack_2389": True,
    }


def build_ir_cert_p2388_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2389_ir_cert_p2389() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2389",
        "name": "Six-Room Protected Rehearsal Runner",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
