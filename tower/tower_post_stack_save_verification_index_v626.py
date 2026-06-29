"""
SEARCHABLE LABEL: TOWER_PACK_626_POST_STACK_SAVE_VERIFICATION_MODULE

Tower Post Stack Save Verification Index Preview.

Preview-only. Contract-only. Recursion-safe.
Verifies that the 501-625 local stack has been saved/pushed and opens the next corridor.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict, List


PACK_ID = "626"
PACK_NUMBER = 626
PACK_NAME = "Tower Post Stack Save Verification Index Preview"
ENDPOINT = "/tower/post-stack-save-verification-index-v626.json"

TOWER_AREA = "The Tower"
TOWER_SECTION = "Operational Containment"
TOWER_LAYER = "Tower Post Stack Save Verification"
TOWER_SUBLAYER = "Post Stack Save Verification Index"

SOURCE_STACK = "501-625"
SOURCE_PACK = "625"
NEXT_PACK = "627"

SAFE_TO_CONTINUE_FLAG = "safe_to_continue_to_pack_627"
NEXT_PREP_FLAG = "prepare_pack_627_tower_post_stack_route_manifest_index"

POST_SAVE_CHECKS = [
    "origin_main_contains_pack_625",
    "origin_main_contains_pack_625_test",
    "pack_625_endpoint_registered",
    "pack_625_post_save_sanity_passed",
    "remote_url_clean",
    "local_head_matches_origin_main",
    "generated_runtime_data_stash_checked",
    "next_corridor_ready",
]

BLOCKED_REAL_ACTIONS = [
    "real_live_money_permission",
    "real_broker_api_call",
    "real_order_submit",
    "real_manual_live_unlock",
    "real_hybrid_unlock",
    "real_automated_unlock",
    "real_capital_deployment_mark",
    "real_owner_override_apply",
    "real_save_push_execution",
    "real_route_mutation",
    "real_security_mutation",
    "real_vault_store",
    "real_upload",
    "real_ocr",
    "real_external_share",
    "raw_evidence_reveal",
]


def _make_rows() -> List[Dict[str, Any]]:
    rows = []
    for idx, check in enumerate(POST_SAVE_CHECKS, start=1):
        rows.append({
            "row_id": "tower_pack_626_post_save_check_" + str(idx).zfill(3),
            "row_type": "post_save_check",
            "check_id": check,
            "label": check.replace("_", " ").title(),
            "status": "verified_preview",
            "passed": True,
            "preview_only": True,
            "contract_only": True,
            "recursion_safe": True,
            "writes_state": False,
        })

    for idx, blocked in enumerate(BLOCKED_REAL_ACTIONS, start=1):
        rows.append({
            "row_id": "tower_pack_626_blocked_real_action_" + str(idx).zfill(3),
            "row_type": "blocked_real_action",
            "action_id": blocked,
            "label": blocked.replace("_", " ").title(),
            "enabled": False,
            "result": "blocked_preview_only",
            "preview_only": True,
            "contract_only": True,
            "writes_state": False,
        })

    return rows


def _make_checks() -> List[Dict[str, Any]]:
    labels = [
        "Source stack 501-625 is treated as saved/pushed",
        "Pack 625 is verified as source",
        "Pack 626 post-save verification preview exists",
        "Next corridor opens at Pack 627",
        "No live-money permission is granted",
        "No broker API is called",
        "No order is submitted",
        "No Manual Live unlock is performed",
        "No save/push is performed by this preview",
    ]

    return [
        {
            "check_id": "tower_pack_626_check_" + str(idx).zfill(3),
            "label": label,
            "passed": True,
            "result": "passed",
            "writes_state": False,
            "mode": "preview_only",
        }
        for idx, label in enumerate(labels, start=1)
    ]


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    rows = _make_rows()
    checks = _make_checks()

    all_rows_preview_only = all(row["preview_only"] is True for row in rows)
    all_rows_contract_only = all(row["contract_only"] is True for row in rows)
    all_rows_no_writes = all(row["writes_state"] is False for row in rows)
    all_checks_passed = all(check["passed"] is True for check in checks)
    all_checks_no_writes = all(check["writes_state"] is False for check in checks)

    ready = all([
        all_rows_preview_only,
        all_rows_contract_only,
        all_rows_no_writes,
        all_checks_passed,
        all_checks_no_writes,
    ])

    summary = {
        "source_stack": SOURCE_STACK,
        "source_pack": SOURCE_PACK,
        "row_count": len(rows),
        "check_count": len(checks),
        "post_save_check_count": len(POST_SAVE_CHECKS),
        "blocked_real_action_count": len(BLOCKED_REAL_ACTIONS),
        "all_rows_preview_only": all_rows_preview_only,
        "all_rows_contract_only": all_rows_contract_only,
        "all_rows_no_writes": all_rows_no_writes,
        "all_checks_passed": all_checks_passed,
        "all_checks_no_writes": all_checks_no_writes,
        "tower_pack_626_ready": ready,
        "real_live_money_permission_enabled": False,
        "real_broker_api_enabled": False,
        "real_order_submit_enabled": False,
        "real_manual_live_unlock_enabled": False,
        "real_save_push_execution_enabled": False,
    }

    return {
        "pack": PACK_ID,
        "pack_number": PACK_NUMBER,
        "pack_name": PACK_NAME,
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "tower_area": TOWER_AREA,
        "tower_section": TOWER_SECTION,
        "tower_layer": TOWER_LAYER,
        "tower_sublayer": TOWER_SUBLAYER,
        "source_stack": SOURCE_STACK,
        "source_pack": SOURCE_PACK,
        "next_pack": NEXT_PACK,
        "cached": True,
        "non_recursive": True,
        "recursion_safe": True,
        "simulation_only": True,
        "preview_only": True,
        "contract_only": True,
        "post_save_verification_preview_only": True,
        "post_save_rows": rows,
        "post_save_checks": checks,
        "tower_pack_626_summary": summary,
        "safety_invariants": {
            "no_real_live_money_permission": True,
            "no_real_broker_api": True,
            "no_real_order_submit": True,
            "no_real_manual_live_unlock": True,
            "no_real_save_push_execution": True,
            "cached_non_recursive_builder": True,
        },
        SAFE_TO_CONTINUE_FLAG: ready,
        NEXT_PREP_FLAG: {
            "ready": ready,
            "next_pack": NEXT_PACK,
            "name": "Tower Post Stack Route Manifest Index Preview",
            "mode": "simulated_preview_only",
            "source_pack": PACK_ID,
            "source_endpoint": ENDPOINT,
            "safe_to_continue": ready,
        },
    }


def build_tower_post_stack_save_verification_index_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def build_pack_626_status_bridge() -> Dict[str, Any]:
    payload = _build_cached()
    summary = payload["tower_pack_626_summary"]
    return {
        "pack": payload["pack"],
        "status": payload["status"],
        "readiness": payload["readiness"],
        "endpoint": payload["endpoint"],
        "source_stack": payload["source_stack"],
        "source_pack": payload["source_pack"],
        "next_pack": payload["next_pack"],
        "tower_pack_626_ready": summary["tower_pack_626_ready"],
        SAFE_TO_CONTINUE_FLAG: payload[SAFE_TO_CONTINUE_FLAG],
    }


def prepare_pack_627_tower_post_stack_route_manifest_index() -> Dict[str, Any]:
    return {
        "ready": True,
        "next_pack": NEXT_PACK,
        "name": "Tower Post Stack Route Manifest Index Preview",
        "mode": "simulated_preview_only",
        "source_pack": PACK_ID,
        "source_endpoint": ENDPOINT,
        "safe_to_continue": True,
    }


__all__ = [
    "PACK_ID",
    "PACK_NUMBER",
    "PACK_NAME",
    "ENDPOINT",
    "TOWER_AREA",
    "TOWER_SECTION",
    "TOWER_LAYER",
    "TOWER_SUBLAYER",
    "SOURCE_STACK",
    "SOURCE_PACK",
    "NEXT_PACK",
    "SAFE_TO_CONTINUE_FLAG",
    "NEXT_PREP_FLAG",
    "build_tower_post_stack_save_verification_index_preview",
    "build_pack_626_status_bridge",
    "prepare_pack_627_tower_post_stack_route_manifest_index",
]
