"""
SEARCHABLE LABEL: TOWER_PACK_2399_SIX_ROOM_ENFORCEMENT

Pack 2399 — Six-Room Enforcement Rehearsal
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict, List

from tower.tower_ir_cert_p2389 import (
    ROOM_REQUESTS,
    run_protected_room_integration,
)
from tower.tower_ir_cert_p2392 import (
    transition_launch_authorization,
)
from tower.tower_ir_cert_p2393 import (
    enforce_protected_ob_route,
)
from tower.tower_ir_cert_p2394 import (
    create_authorization_denial_receipt,
)
from tower.tower_ir_cert_p2395 import (
    create_launch_use_receipt,
)
from tower.tower_ir_cert_p2396 import (
    verify_launch_receipt_chain,
)
from tower.tower_ir_cert_p2397 import (
    create_emergency_lockback,
)
from tower.tower_ir_cert_p2398 import (
    build_owner_session_audit,
)


PACK_ID = "2399"
ENDPOINT = "/tower/ir-cert-v2399.json"


def run_room_enforcement_rehearsal(
    *,
    request: Dict[str, Any],
    rehearsal_index: int,
) -> Dict[str, Any]:
    base = run_protected_room_integration(
        requested_path=request["path"],
        mode=request["mode"],
        object_context=request["object_context"],
        rehearsal_index=rehearsal_index,
    )

    handoff = base["handoff"]
    decision = base["decision_envelope"]

    enforcement = enforce_protected_ob_route(
        decision_envelope=decision,
        handoff=handoff,
        owner_id=handoff["owner_id"],
        session_id=handoff["session_id"],
        requested_room_id=handoff["approved_room_id"],
        requested_path=handoff["canonical_path"],
        requested_mode=handoff["mode"],
        evaluation_time="2026-07-14T12:00:01+00:00",
        consumed_handoff_ids=[],
        revoked_handoff_ids=[],
    )

    consume = transition_launch_authorization(
        handoff_id=handoff["handoff_id"],
        current_state="active_preview",
        requested_action="consume",
        reason_code="ob_launch_authorization_consumed",
        event_time="2026-07-14T12:00:02+00:00",
    )

    use_receipt = create_launch_use_receipt(
        handoff=handoff,
        enforcement_decision=enforcement,
        used_at="2026-07-14T12:00:02+00:00",
        state_transition_reference=(
            consume["state_transition_reference"]
        ),
    )

    receipt_chain = verify_launch_receipt_chain(
        handoff=handoff,
        launch_use_receipt=use_receipt,
        room_access_receipt=base["access_receipt"],
        completion_intake=base["completion_intake"],
        close_receipt=base["close_receipt"],
    )

    replay_attempt = enforce_protected_ob_route(
        decision_envelope=decision,
        handoff=handoff,
        owner_id=handoff["owner_id"],
        session_id=handoff["session_id"],
        requested_room_id=handoff["approved_room_id"],
        requested_path=handoff["canonical_path"],
        requested_mode=handoff["mode"],
        evaluation_time="2026-07-14T12:00:03+00:00",
        consumed_handoff_ids=[handoff["handoff_id"]],
        revoked_handoff_ids=[],
    )

    denial_receipt = create_authorization_denial_receipt(
        request_id=base["bridge_request"]["request_id"],
        owner_id=handoff["owner_id"],
        session_id=handoff["session_id"],
        requested_room_id=handoff["approved_room_id"],
        requested_path=handoff["canonical_path"],
        requested_mode=handoff["mode"],
        reason_code=replay_attempt["reason_code"],
        denied_at="2026-07-14T12:00:03+00:00",
        handoff_id=handoff["handoff_id"],
    )

    audit = build_owner_session_audit(
        handoff=handoff,
        enforcement_decision=enforcement,
        launch_use_receipt=use_receipt,
        completion_intake=base["completion_intake"],
        close_receipt=base["close_receipt"],
        denial_receipt=denial_receipt,
    )

    passed = all([
        base["status"] == "passed",
        enforcement["allowed"],
        consume["allowed"],
        consume["next_state"] == "consumed",
        use_receipt["authorization_consumed"],
        receipt_chain["verified"],
        replay_attempt["allowed"] is False,
        replay_attempt["reason_code"]
        == "ob_launch_handoff_replay_blocked",
        denial_receipt["decision"] == "deny",
        audit["final_ob_access_state"] == "locked_back",
        audit["default_deny_restored"] is True,
    ])

    return {
        "room_id": handoff["approved_room_id"],
        "canonical_path": handoff["canonical_path"],
        "status": "passed" if passed else "failed",
        "base_integration": base,
        "enforcement": enforcement,
        "consume_transition": consume,
        "launch_use_receipt": use_receipt,
        "receipt_chain": receipt_chain,
        "replay_attempt": replay_attempt,
        "replay_denial_receipt": denial_receipt,
        "owner_audit_summary": audit,
        "preview_only": True,
        "writes_state": False,
    }


def run_six_room_enforcement_rehearsal() -> Dict[str, Any]:
    rooms: List[Dict[str, Any]] = []

    for index, request in enumerate(
        ROOM_REQUESTS,
        start=1,
    ):
        rooms.append(
            run_room_enforcement_rehearsal(
                request=request,
                rehearsal_index=index,
            )
        )

    emergency_base = rooms[0]["base_integration"]

    emergency = create_emergency_lockback(
        handoff=emergency_base["handoff"],
        trigger_code="owner_emergency_close",
        detected_at="2026-07-14T12:01:00+00:00",
    )

    passed = (
        len(rooms) == 6
        and all(
            room["status"] == "passed"
            for room in rooms
        )
        and emergency["ob_access_state"] == "locked_back"
        and emergency["default_deny_restored"] is True
    )

    return {
        "status": "passed" if passed else "failed",
        "room_count": len(rooms),
        "rooms": rooms,
        "all_rooms_passed": all(
            room["status"] == "passed"
            for room in rooms
        ),
        "emergency_lockback": emergency,
        "replay_blocking_passed": all(
            room["replay_attempt"]["allowed"] is False
            for room in rooms
        ),
        "receipt_chain_passed": all(
            room["receipt_chain"]["verified"]
            for room in rooms
        ),
        "default_deny_restored": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    rehearsal = run_six_room_enforcement_rehearsal()

    return {
        "pack": PACK_ID,
        "pack_name": "Six-Room Enforcement Rehearsal",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "rehearsal": rehearsal,
        "all_six_rooms_passed": (
            rehearsal["all_rooms_passed"]
        ),
        "replay_blocking_passed": (
            rehearsal["replay_blocking_passed"]
        ),
        "receipt_chain_passed": (
            rehearsal["receipt_chain_passed"]
        ),
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2400",
        "safe_to_continue_to_pack_2400": True,
    }


def build_ir_cert_p2399_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2400_ir_cert_p2400() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2400",
        "name": "Enforcement Readiness Checkpoint",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
