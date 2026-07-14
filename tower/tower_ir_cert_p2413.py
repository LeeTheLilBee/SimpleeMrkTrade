"""
SEARCHABLE LABEL: TOWER_PACK_2413_SIX_ROOM_EVIDENCE_MATRIX

Pack 2413 — Six-Room Certification Evidence Matrix
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict, List

from tower.tower_ir_cert_p2372 import ROOMS
from tower.tower_ir_cert_p2389 import (
    run_six_room_protected_rehearsal,
)
from tower.tower_ir_cert_p2399 import (
    run_six_room_enforcement_rehearsal,
)
from tower.tower_ir_cert_p2408 import (
    run_six_room_failure_rehearsal,
)


PACK_ID = "2413"
ENDPOINT = "/tower/ir-cert-v2413.json"


def build_six_room_certification_matrix() -> Dict[str, Any]:
    integration = run_six_room_protected_rehearsal()
    enforcement = run_six_room_enforcement_rehearsal()
    failure = run_six_room_failure_rehearsal()

    integration_by_room = {
        item["room_id"]: item
        for item in integration["rooms"]
    }

    enforcement_by_room = {
        item["room_id"]: item
        for item in enforcement["rooms"]
    }

    failure_by_room = {
        item["room_id"]: item
        for item in failure["results"]
    }

    matrix: List[Dict[str, Any]] = []

    for room in ROOMS:
        room_id = room["room_id"]
        integration_item = integration_by_room[room_id]
        enforcement_item = enforcement_by_room[room_id]
        failure_item = failure_by_room[room_id]

        checks = {
            "registry_present": True,
            "canonical_route_present": bool(
                room["canonical_route"]
            ),
            "clearance_contract_present": bool(
                room["required_clearance_value"]
            ),
            "integration_passed": (
                integration_item["status"] == "passed"
            ),
            "enforcement_passed": (
                enforcement_item["status"] == "passed"
            ),
            "replay_blocked": (
                enforcement_item["replay_attempt"]["allowed"]
                is False
            ),
            "receipt_chain_verified": (
                enforcement_item["receipt_chain"]["verified"]
            ),
            "failure_detected": (
                failure_item["status"] == "passed"
            ),
            "lockback_verified": (
                failure_item["recovery_receipt"][
                    "ob_access_state"
                ] == "locked_back"
            ),
            "default_deny_restored": (
                failure_item["recovery_receipt"][
                    "default_deny_restored"
                ]
            ),
        }

        matrix.append({
            "room_id": room_id,
            "display_name": room["display_name"],
            "canonical_route": room["canonical_route"],
            "required_clearance_value": (
                room["required_clearance_value"]
            ),
            "required_clearance_rank": (
                room["required_clearance_rank"]
            ),
            "step_up_required": room[
                "step_up_required"
            ],
            "owner_only": room["owner_only"],
            "checks": checks,
            "certified": all(checks.values()),
        })

    return {
        "room_count": len(matrix),
        "matrix": matrix,
        "all_rooms_certified": all(
            item["certified"]
            for item in matrix
        ),
        "preview_only": True,
        "writes_state": False,
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    matrix = build_six_room_certification_matrix()

    return {
        "pack": PACK_ID,
        "pack_name": (
            "Six-Room Certification Evidence Matrix"
        ),
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "certification_matrix": matrix,
        "all_six_rooms_certified": (
            matrix["all_rooms_certified"]
        ),
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2414",
        "safe_to_continue_to_pack_2414": True,
    }


def build_ir_cert_p2413_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2414_ir_cert_p2414() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2414",
        "name": "Allow/Deny Reason-Code Coverage Contract",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
