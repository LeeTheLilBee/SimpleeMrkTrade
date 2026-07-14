"""
SEARCHABLE LABEL: TOWER_PACK_2389_SIX_ROOM_INTEGRATION_RUNNER

Pack 2389 — Six-Room Protected Rehearsal Runner
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict, List

from tower.tower_ir_cert_p2372 import get_room_by_id
from tower.tower_ir_cert_p2373 import resolve_observatory_route
from tower.tower_ir_cert_p2374 import translate_tower_clearance
from tower.tower_ir_cert_p2375 import evaluate_room_access
from tower.tower_ir_cert_p2376 import (
    build_protected_room_manifest,
)
from tower.tower_ir_cert_p2377 import (
    create_ob_launch_handoff,
)
from tower.tower_ir_cert_p2378 import (
    create_room_access_receipt,
)
from tower.tower_ir_cert_p2379 import (
    close_ob_launch_session,
)
from tower.tower_ir_cert_p2381 import (
    build_protected_bridge_request,
)
from tower.tower_ir_cert_p2382 import (
    adapt_pack_101_bridge_request,
)
from tower.tower_ir_cert_p2383 import (
    build_room_decision_envelope,
)
from tower.tower_ir_cert_p2384 import (
    validate_ob_launch_authorization,
)
from tower.tower_ir_cert_p2385 import (
    evaluate_handoff_replay_guard,
)
from tower.tower_ir_cert_p2386 import (
    evaluate_cross_room_scope,
)
from tower.tower_ir_cert_p2387 import (
    intake_ob_completion_receipt,
)
from tower.tower_ir_cert_p2388 import (
    verify_ob_lockback,
)


PACK_ID = "2389"
ENDPOINT = "/tower/ir-cert-v2389.json"


ROOM_REQUESTS = [
    {
        "path": "/dashboard",
        "mode": "paper",
        "object_context": {},
    },
    {
        "path": "/market-map",
        "mode": "paper",
        "object_context": {},
    },
    {
        "path": "/symbol/AMD",
        "mode": "paper",
        "object_context": {"symbol": "AMD"},
    },
    {
        "path": "/trade-center",
        "mode": "paper",
        "object_context": {
            "mission_account_id": "proof_demo",
        },
    },
    {
        "path": "/review-center",
        "mode": "paper",
        "object_context": {
            "mission_account_id": "proof_demo",
        },
    },
    {
        "path": "/owner-console",
        "mode": "paper",
        "object_context": {
            "mission_account_id": "proof_demo",
        },
    },
]


def run_protected_room_integration(
    *,
    requested_path: str,
    mode: str,
    object_context: Dict[str, Any],
    rehearsal_index: int,
) -> Dict[str, Any]:
    owner_id = "owner_rehearsal"
    session_id = f"session_{rehearsal_index:02d}"
    step_up_reference = f"stepup_{rehearsal_index:02d}"

    pack_101 = adapt_pack_101_bridge_request({
        "bridge_request_type": (
            "canonical_observatory_bridge_request"
        ),
        "request_id": f"request_{rehearsal_index:02d}",
        "owner_id": owner_id,
        "session_id": session_id,
        "app_id": "ob",
        "preferred_route": requested_path,
        "mode": mode,
        "tower_role": "owner",
        "object_context": object_context,
    })

    bridge_request = pack_101["canonical_request"]

    route = resolve_observatory_route(requested_path)

    clearance = translate_tower_clearance(
        subject_id=owner_id,
        tower_role="owner",
        identity_verified=True,
        account_active=True,
        risk_state="acceptable",
        lockdown_state="tower_guarded_default_deny",
    )

    room = get_room_by_id(route["room_id"])

    access = evaluate_room_access(
        room_id=room["room_id"],
        tower_role="owner",
        canonical_clearance_value=(
            clearance["canonical_clearance_value"]
        ),
        canonical_clearance_rank=(
            clearance["canonical_clearance_rank"]
        ),
        identity_verified=True,
        risk_state="acceptable",
        lockdown_active=False,
        mode=mode,
        step_up_reference=step_up_reference,
        step_up_valid=True,
        object_context=object_context,
    )

    manifest_context = {
        "ob_room_symbol_page": {"symbol": "AMD"},
        "ob_room_trade_center": {
            "mission_account_id": "proof_demo",
        },
        "ob_room_review_center": {
            "mission_account_id": "proof_demo",
        },
        "ob_room_owner_console": {
            "mission_account_id": "proof_demo",
        },
    }

    manifest = build_protected_room_manifest(
        tower_role="owner",
        canonical_clearance_value=(
            clearance["canonical_clearance_value"]
        ),
        canonical_clearance_rank=(
            clearance["canonical_clearance_rank"]
        ),
        identity_verified=True,
        risk_state="acceptable",
        lockdown_active=False,
        mode=mode,
        step_up_reference=step_up_reference,
        step_up_valid=True,
        object_context_by_room=manifest_context,
    )

    decision = build_room_decision_envelope(
        bridge_request=bridge_request,
        route_decision=route,
        clearance_decision=clearance,
        room_access_decision=access,
    )

    handoff = create_ob_launch_handoff(
        owner_id=owner_id,
        session_id=session_id,
        approved_room=room,
        canonical_path=route["canonical_path"],
        mode=mode,
        step_up_reference=(
            step_up_reference
            if room["step_up_required"]
            else None
        ),
        clearance_decision_reference=(
            clearance["clearance_decision_reference"]
        ),
        issued_at="2026-07-14T12:00:00+00:00",
    )

    launch_validation = validate_ob_launch_authorization(
        decision_envelope=decision,
        handoff=handoff,
        owner_id=owner_id,
        session_id=session_id,
        requested_path=route["canonical_path"],
        requested_mode=mode,
    )

    replay_guard = evaluate_handoff_replay_guard(
        handoff=handoff,
        evaluation_time="2026-07-14T12:00:01+00:00",
        consumed_handoff_ids=[],
        revoked_handoff_ids=[],
    )

    room_scope = evaluate_cross_room_scope(
        handoff=handoff,
        requested_room_id=room["room_id"],
        requested_path=route["canonical_path"],
        requested_mode=mode,
        requested_session_id=session_id,
    )

    access_receipt = create_room_access_receipt(
        handoff=handoff,
        bridge_decision=decision["reason_code"],
        clearance_value=(
            clearance["canonical_clearance_value"]
        ),
        clearance_rank=(
            clearance["canonical_clearance_rank"]
        ),
        step_up_state=(
            "validated"
            if room["step_up_required"]
            else "not_required"
        ),
        launch_time="2026-07-14T12:00:02+00:00",
    )

    completion = intake_ob_completion_receipt(
        handoff=handoff,
        ob_completion_payload={
            "handoff_id": handoff["handoff_id"],
            "session_id": session_id,
            "room_id": room["room_id"],
            "canonical_path": route["canonical_path"],
            "completion_state": "completed_preview",
            "completion_time": (
                "2026-07-14T12:04:59+00:00"
            ),
            "ob_receipt_reference": (
                f"ob_completion_{rehearsal_index:02d}"
            ),
        },
    )

    close_receipt = close_ob_launch_session(
        handoff=handoff,
        access_receipt=access_receipt,
        close_time="2026-07-14T12:05:00+00:00",
        close_reason="protected_rehearsal_complete",
    )

    lockback = verify_ob_lockback(
        handoff=handoff,
        completion_intake=completion,
        close_receipt=close_receipt,
    )

    passed = all([
        pack_101["adapted"],
        bridge_request["valid"],
        route["allowed"],
        clearance["allowed"],
        access["allowed"],
        room["room_id"] in {
            item["room_id"]
            for item in manifest["available_rooms"]
        },
        decision["allowed"],
        launch_validation["allowed"],
        replay_guard["allowed"],
        room_scope["allowed"],
        completion["accepted"],
        lockback["verified"],
    ])

    return {
        "path": requested_path,
        "room_id": room["room_id"],
        "status": "passed" if passed else "failed",
        "pack_101_adapter": pack_101,
        "bridge_request": bridge_request,
        "route_decision": route,
        "clearance_decision": clearance,
        "room_access_decision": access,
        "manifest_room_present": (
            room["room_id"] in {
                item["room_id"]
                for item in manifest["available_rooms"]
            }
        ),
        "decision_envelope": decision,
        "handoff": handoff,
        "launch_validation": launch_validation,
        "replay_guard": replay_guard,
        "room_scope": room_scope,
        "access_receipt": access_receipt,
        "completion_intake": completion,
        "close_receipt": close_receipt,
        "lockback_verification": lockback,
        "preview_only": True,
        "writes_state": False,
    }


def run_six_room_protected_rehearsal() -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []

    for index, request in enumerate(
        ROOM_REQUESTS,
        start=1,
    ):
        results.append(
            run_protected_room_integration(
                requested_path=request["path"],
                mode=request["mode"],
                object_context=request["object_context"],
                rehearsal_index=index,
            )
        )

    unmapped = resolve_observatory_route(
        "/unmapped-protected-room"
    )

    passed = (
        len(results) == 6
        and all(
            result["status"] == "passed"
            for result in results
        )
        and unmapped["allowed"] is False
        and unmapped["reason_code"]
        == "ob_route_unmapped_default_deny"
    )

    return {
        "status": "passed" if passed else "failed",
        "room_count": len(results),
        "rooms": results,
        "unmapped_route_test": unmapped,
        "all_rooms_passed": all(
            result["status"] == "passed"
            for result in results
        ),
        "default_deny_passed": (
            unmapped["reason_code"]
            == "ob_route_unmapped_default_deny"
        ),
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    rehearsal = run_six_room_protected_rehearsal()

    return {
        "pack": PACK_ID,
        "pack_name": "Six-Room Protected Rehearsal Runner",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "rehearsal": rehearsal,
        "all_six_rooms_passed": (
            rehearsal["status"] == "passed"
        ),
        "default_deny_passed": (
            rehearsal["default_deny_passed"]
        ),
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2390",
        "safe_to_continue_to_pack_2390": True,
    }


def build_ir_cert_p2389_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2390_ir_cert_p2390() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2390",
        "name": (
            "Protected Launch Integration Readiness Checkpoint"
        ),
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
