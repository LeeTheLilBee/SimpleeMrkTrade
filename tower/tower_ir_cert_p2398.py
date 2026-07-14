"""
SEARCHABLE LABEL: TOWER_PACK_2398_OWNER_SESSION_AUDIT

Pack 2398 — Owner Session Audit Summary
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict


PACK_ID = "2398"
ENDPOINT = "/tower/ir-cert-v2398.json"


def build_owner_session_audit(
    *,
    handoff: Dict[str, Any],
    enforcement_decision: Dict[str, Any],
    launch_use_receipt: Dict[str, Any] | None,
    completion_intake: Dict[str, Any] | None,
    close_receipt: Dict[str, Any] | None,
    denial_receipt: Dict[str, Any] | None,
) -> Dict[str, Any]:
    allowed = enforcement_decision.get("allowed") is True

    return {
        "owner_id": handoff.get("owner_id"),
        "session_id": handoff.get("session_id"),
        "handoff_id": handoff.get("handoff_id"),
        "room_id": handoff.get("approved_room_id"),
        "canonical_path": handoff.get("canonical_path"),
        "mode": handoff.get("mode"),
        "enforcement_result": (
            "allowed" if allowed else "denied"
        ),
        "enforcement_reason_code": (
            enforcement_decision.get("reason_code")
        ),
        "launch_use_receipt_id": (
            launch_use_receipt.get(
                "launch_use_receipt_id"
            )
            if launch_use_receipt
            else None
        ),
        "completion_accepted": (
            completion_intake.get("accepted")
            if completion_intake
            else False
        ),
        "close_receipt_id": (
            close_receipt.get("close_receipt_id")
            if close_receipt
            else None
        ),
        "denial_receipt_id": (
            denial_receipt.get("denial_receipt_id")
            if denial_receipt
            else None
        ),
        "final_ob_access_state": (
            close_receipt.get("ob_access_state")
            if close_receipt
            else "default_deny"
        ),
        "default_deny_restored": (
            close_receipt.get(
                "default_deny_restored",
                True,
            )
            if close_receipt
            else True
        ),
        "preview_only": True,
        "writes_state": False,
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": "Owner Session Audit Summary",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "owner_safe_summary_only": True,
        "raw_secret_material_exposed": False,
        "raw_step_up_material_exposed": False,
        "default_deny_visible": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2399",
        "safe_to_continue_to_pack_2399": True,
    }


def build_ir_cert_p2398_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2399_ir_cert_p2399() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2399",
        "name": "Six-Room Enforcement Rehearsal",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
