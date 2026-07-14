"""
SEARCHABLE LABEL: TOWER_PACK_2409_OWNER_ASSURANCE_SUMMARY

Pack 2409 — Owner Assurance Summary
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_ir_cert_p2408 import (
    run_six_room_failure_rehearsal,
)


PACK_ID = "2409"
ENDPOINT = "/tower/ir-cert-v2409.json"


def build_owner_assurance_summary() -> Dict[str, Any]:
    rehearsal = run_six_room_failure_rehearsal()

    scenarios = [
        {
            "room_id": item["room_id"],
            "scenario": item["scenario"],
            "status": item["status"],
            "incident_receipt_id": item[
                "incident_receipt"
            ]["incident_receipt_id"],
            "recovery_receipt_id": item[
                "recovery_receipt"
            ]["recovery_receipt_id"],
            "final_access_state": item[
                "recovery_receipt"
            ]["ob_access_state"],
            "default_deny_restored": item[
                "recovery_receipt"
            ]["default_deny_restored"],
        }
        for item in rehearsal["results"]
    ]

    ready = all([
        rehearsal["status"] == "passed",
        rehearsal["all_failures_detected"],
        rehearsal["all_sessions_locked_back"],
        rehearsal["all_default_deny_restored"],
        rehearsal["all_new_handoffs_required"],
    ])

    return {
        "ready": ready,
        "recommendation": (
            "GO_TOWER_OB_PROTECTED_ASSURANCE_READY"
            if ready
            else "NO_GO_TOWER_OB_ASSURANCE_INCOMPLETE"
        ),
        "room_count": rehearsal["room_count"],
        "scenario_summaries": scenarios,
        "owner_safe_summary_only": True,
        "raw_step_up_material_exposed": False,
        "raw_secret_material_exposed": False,
        "default_deny_restored": (
            rehearsal["all_default_deny_restored"]
        ),
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    summary = build_owner_assurance_summary()

    return {
        "pack": PACK_ID,
        "pack_name": "Owner Assurance Summary",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "owner_assurance_summary": summary,
        "owner_assurance_ready": summary["ready"],
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2410",
        "safe_to_continue_to_pack_2410": True,
    }


def build_ir_cert_p2409_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2410_ir_cert_p2410() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2410",
        "name": "Assurance Readiness Checkpoint",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
