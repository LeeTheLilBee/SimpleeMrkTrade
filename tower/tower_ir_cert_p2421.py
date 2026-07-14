"""
SEARCHABLE LABEL:
TOWER_PACK_2421_PROTECTED_LAUNCH_OPERATIONAL_VALIDATION

Pack 2421 — Protected Launch Operational Validation

Runs repeated preview-only owner sessions across all six
Observatory rooms and validates:

- Canonical and alias route resolution
- Tower owner-clearance translation
- Protected manifest filtering
- Launch handoff scope
- Single-use enforcement
- Completion receipt intake
- Session close and lockback
- Replay denial
- Failure recovery
- Certification seal continuity
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict, List

from tower.tower_ir_cert_p2372 import ROOMS
from tower.tower_ir_cert_p2373 import (
    resolve_observatory_route,
)
from tower.tower_ir_cert_p2389 import (
    run_protected_room_integration,
)
from tower.tower_ir_cert_p2399 import (
    run_room_enforcement_rehearsal,
)
from tower.tower_ir_cert_p2408 import (
    FAILURE_SCENARIOS,
    run_failure_injection,
)
from tower.tower_ir_cert_p2419 import (
    run_final_certification_rehearsal,
)


PACK_ID = "2421"
ENDPOINT = "/tower/ir-cert-v2421.json"

VALIDATION_CYCLES_PER_ROOM = 3


def _canonical_request_for_room(
    room: Dict[str, Any],
) -> Dict[str, Any]:
    if room["room_id"] == "ob_room_symbol_page":
        path = "/symbol/AMD"
        object_context = {
            "symbol": "AMD",
        }

    elif room["object_guard"]["required"]:
        path = room["canonical_route"]
        object_context = {
            "mission_account_id": "proof_demo",
        }

    else:
        path = room["canonical_route"]
        object_context = {}

    return {
        "path": path,
        "mode": "paper",
        "object_context": object_context,
    }


def _alias_request_for_room(
    room: Dict[str, Any],
) -> str:
    alias = room["accepted_aliases"][0]

    if "<symbol>" in alias:
        return alias.replace("<symbol>", "AMD")

    return alias


def run_room_operational_validation(
    *,
    room: Dict[str, Any],
    room_index: int,
) -> Dict[str, Any]:
    request = _canonical_request_for_room(room)

    alias_path = _alias_request_for_room(room)

    canonical_resolution = resolve_observatory_route(
        request["path"]
    )

    alias_resolution = resolve_observatory_route(
        alias_path
    )

    cycles: List[Dict[str, Any]] = []

    for cycle in range(
        1,
        VALIDATION_CYCLES_PER_ROOM + 1,
    ):
        rehearsal_index = (
            room_index * 10
            + cycle
        )

        integration = run_protected_room_integration(
            requested_path=request["path"],
            mode=request["mode"],
            object_context=request["object_context"],
            rehearsal_index=rehearsal_index,
        )

        enforcement = run_room_enforcement_rehearsal(
            request=request,
            rehearsal_index=rehearsal_index + 100,
        )

        cycle_passed = all([
            integration["status"] == "passed",
            enforcement["status"] == "passed",
            integration["clearance_decision"][
                "canonical_clearance_value"
            ] == "ob_owner_command",
            integration["clearance_decision"][
                "canonical_clearance_rank"
            ] == 900,
            integration["launch_validation"][
                "allowed"
            ],
            integration["completion_intake"][
                "accepted"
            ],
            integration["lockback_verification"][
                "verified"
            ],
            enforcement["enforcement"]["allowed"],
            enforcement["consume_transition"][
                "next_state"
            ] == "consumed",
            enforcement["replay_attempt"][
                "allowed"
            ] is False,
            enforcement["receipt_chain"][
                "verified"
            ],
            enforcement["owner_audit_summary"][
                "final_ob_access_state"
            ] == "locked_back",
        ])

        cycles.append({
            "cycle": cycle,
            "status": (
                "passed"
                if cycle_passed
                else "failed"
            ),
            "handoff_id": integration[
                "handoff"
            ]["handoff_id"],
            "access_receipt_id": integration[
                "access_receipt"
            ]["receipt_id"],
            "close_receipt_id": integration[
                "close_receipt"
            ]["close_receipt_id"],
            "launch_use_receipt_id": enforcement[
                "launch_use_receipt"
            ]["launch_use_receipt_id"],
            "replay_denial_receipt_id": enforcement[
                "replay_denial_receipt"
            ]["denial_receipt_id"],
            "final_access_state": enforcement[
                "owner_audit_summary"
            ]["final_ob_access_state"],
            "default_deny_restored": enforcement[
                "owner_audit_summary"
            ]["default_deny_restored"],
        })

    failure_scenario = FAILURE_SCENARIOS[
        (room_index - 1) % len(FAILURE_SCENARIOS)
    ]

    failure = run_failure_injection(
        request=request,
        scenario=failure_scenario,
        rehearsal_index=room_index + 300,
    )

    passed = all([
        canonical_resolution["allowed"],
        alias_resolution["allowed"],
        canonical_resolution["room_id"]
        == room["room_id"],
        alias_resolution["room_id"]
        == room["room_id"],
        alias_resolution["canonical_path"]
        == canonical_resolution["canonical_path"],
        len(cycles)
        == VALIDATION_CYCLES_PER_ROOM,
        all(
            cycle["status"] == "passed"
            for cycle in cycles
        ),
        failure["status"] == "passed",
        failure["recovery_receipt"][
            "ob_access_state"
        ] == "locked_back",
        failure["recovery_receipt"][
            "default_deny_restored"
        ] is True,
        failure["recovery_receipt"][
            "new_handoff_required"
        ] is True,
    ])

    return {
        "room_id": room["room_id"],
        "display_name": room["display_name"],
        "canonical_request_path": request["path"],
        "alias_request_path": alias_path,
        "canonical_resolution": canonical_resolution,
        "alias_resolution": alias_resolution,
        "cycle_count": len(cycles),
        "cycles": cycles,
        "failure_scenario": failure_scenario[
            "incident_type"
        ],
        "failure_validation": failure,
        "status": "passed" if passed else "failed",
        "preview_only": True,
        "writes_state": False,
    }


def run_protected_launch_operational_validation(
) -> Dict[str, Any]:
    rooms: List[Dict[str, Any]] = []

    for index, room in enumerate(
        ROOMS,
        start=1,
    ):
        rooms.append(
            run_room_operational_validation(
                room=room,
                room_index=index,
            )
        )

    certification = (
        run_final_certification_rehearsal()
    )

    unmapped = resolve_observatory_route(
        "/operational-validation-unmapped-room"
    )

    total_cycles = sum(
        room["cycle_count"]
        for room in rooms
    )

    unique_handoffs = {
        cycle["handoff_id"]
        for room in rooms
        for cycle in room["cycles"]
    }

    checks = {
        "six_rooms_present": len(rooms) == 6,
        "all_rooms_passed": all(
            room["status"] == "passed"
            for room in rooms
        ),
        "expected_cycle_count": (
            total_cycles
            == 6 * VALIDATION_CYCLES_PER_ROOM
        ),
        "all_handoffs_unique": (
            len(unique_handoffs) == total_cycles
        ),
        "all_cycles_locked_back": all(
            cycle["final_access_state"]
            == "locked_back"
            for room in rooms
            for cycle in room["cycles"]
        ),
        "all_default_deny_restored": all(
            cycle["default_deny_restored"]
            for room in rooms
            for cycle in room["cycles"]
        ),
        "all_failure_recoveries_passed": all(
            room["failure_validation"]["status"]
            == "passed"
            for room in rooms
        ),
        "unmapped_route_blocked": (
            unmapped["allowed"] is False
            and unmapped["reason_code"]
            == "ob_route_unmapped_default_deny"
        ),
        "certification_seal_valid": (
            certification["seal_verification"][
                "valid"
            ]
        ),
        "production_authorization_not_granted": (
            certification[
                "production_authorization_granted"
            ] is False
        ),
    }

    passed = all(checks.values())

    return {
        "status": "passed" if passed else "failed",
        "recommendation": (
            "GO_TOWER_OB_OPERATIONAL_PREVIEW_VALIDATED"
            if passed
            else "NO_GO_TOWER_OB_OPERATIONAL_VALIDATION_INCOMPLETE"
        ),
        "room_count": len(rooms),
        "cycles_per_room": (
            VALIDATION_CYCLES_PER_ROOM
        ),
        "total_session_cycles": total_cycles,
        "unique_handoff_count": len(
            unique_handoffs
        ),
        "rooms": rooms,
        "unmapped_route_test": unmapped,
        "certification_reference": {
            "certification_seal_id": (
                certification[
                    "certification_seal"
                ]["certification_seal_id"]
            ),
            "seal_valid": certification[
                "seal_verification"
            ]["valid"],
        },
        "checks": checks,
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
    validation = (
        run_protected_launch_operational_validation()
    )

    return {
        "pack": PACK_ID,
        "pack_name": (
            "Protected Launch Operational Validation"
        ),
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "operational_validation": validation,
        "operational_preview_validated": (
            validation["status"] == "passed"
        ),
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2422",
        "safe_to_continue_to_pack_2422": True,
    }


def build_ir_cert_p2421_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2422_ir_cert_p2422() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2422",
        "name": (
            "Observatory Protected Launch Corridor Closeout"
        ),
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
