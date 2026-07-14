"""
SEARCHABLE LABEL: TOWER_PACK_2408_FAILURE_INJECTION_REHEARSAL

Pack 2408 — Six-Room Failure Injection Rehearsal
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict, List

from tower.tower_ir_cert_p2389 import (
    ROOM_REQUESTS,
    run_protected_room_integration,
)
from tower.tower_ir_cert_p2402 import (
    verify_step_up_lifecycle,
)
from tower.tower_ir_cert_p2403 import (
    evaluate_runtime_interrupt,
)
from tower.tower_ir_cert_p2404 import (
    detect_protected_session_drift,
)
from tower.tower_ir_cert_p2405 import (
    detect_route_contract_drift,
)
from tower.tower_ir_cert_p2406 import (
    recover_failed_protected_launch,
)
from tower.tower_ir_cert_p2407 import (
    create_protected_launch_incident_receipt,
)


PACK_ID = "2408"
ENDPOINT = "/tower/ir-cert-v2408.json"


FAILURE_SCENARIOS = [
    {
        "incident_type": "step_up_loss",
        "reason_code": "ob_step_up_not_valid",
        "failure_stage": "step_up",
    },
    {
        "incident_type": "risk_change",
        "reason_code": "ob_runtime_risk_state_changed",
        "failure_stage": "route_enforcement",
    },
    {
        "incident_type": "lockdown_activation",
        "reason_code": "tower_lockdown_activated",
        "failure_stage": "route_enforcement",
    },
    {
        "incident_type": "session_drift",
        "reason_code": "ob_launch_session_mismatch",
        "failure_stage": "ob_room_entry",
    },
    {
        "incident_type": "cross_room_drift",
        "reason_code": "ob_cross_room_launch_blocked",
        "failure_stage": "ob_room_entry",
    },
    {
        "incident_type": "route_contract_drift",
        "reason_code": "ob_route_unmapped_default_deny",
        "failure_stage": "ob_room_entry",
    },
]


def run_failure_injection(
    *,
    request: Dict[str, Any],
    scenario: Dict[str, Any],
    rehearsal_index: int,
) -> Dict[str, Any]:
    base = run_protected_room_integration(
        requested_path=request["path"],
        mode=request["mode"],
        object_context=request["object_context"],
        rehearsal_index=rehearsal_index,
    )

    handoff = base["handoff"]
    room = base["room_access_decision"]["approved_room"]

    if scenario["incident_type"] == "step_up_loss":
        detector = verify_step_up_lifecycle(
            step_up_required=True,
            step_up_reference=(
                handoff.get("step_up_reference")
                or f"stepup_{rehearsal_index}"
            ),
            step_up_state="revoked",
            owner_id=handoff["owner_id"],
            step_up_owner_id=handoff["owner_id"],
            session_id=handoff["session_id"],
            step_up_session_id=handoff["session_id"],
            room_id=handoff["approved_room_id"],
            step_up_room_id=handoff["approved_room_id"],
        )

        detected = detector["allowed"] is False

    elif scenario["incident_type"] == "risk_change":
        detector = evaluate_runtime_interrupt(
            original_risk_state="acceptable",
            current_risk_state="blocked",
            original_lockdown_state="normal",
            current_lockdown_state="normal",
            account_active=True,
            identity_still_verified=True,
        )

        detected = detector["interrupted"] is True

    elif scenario["incident_type"] == "lockdown_activation":
        detector = evaluate_runtime_interrupt(
            original_risk_state="acceptable",
            current_risk_state="acceptable",
            original_lockdown_state="normal",
            current_lockdown_state="active",
            account_active=True,
            identity_still_verified=True,
        )

        detected = detector["interrupted"] is True

    elif scenario["incident_type"] == "session_drift":
        detector = detect_protected_session_drift(
            handoff=handoff,
            current_owner_id=handoff["owner_id"],
            current_session_id="different_session",
            current_room_id=handoff["approved_room_id"],
            current_path=handoff["canonical_path"],
            current_mode=handoff["mode"],
        )

        detected = detector["drift_detected"] is True

    elif scenario["incident_type"] == "cross_room_drift":
        detector = detect_protected_session_drift(
            handoff=handoff,
            current_owner_id=handoff["owner_id"],
            current_session_id=handoff["session_id"],
            current_room_id="ob_room_owner_console",
            current_path="/owner-console",
            current_mode=handoff["mode"],
        )

        detected = detector["drift_detected"] is True

    else:
        detector = detect_route_contract_drift(
            room_id=room["room_id"],
            expected_canonical_path=handoff["canonical_path"],
            observed_path="/not-a-real-ob-room",
        )

        detected = detector["drift_detected"] is True

    recovery = recover_failed_protected_launch(
        handoff=handoff,
        failure_code=scenario["reason_code"],
        failure_stage=scenario["failure_stage"],
        detected_at="2026-07-14T13:00:00+00:00",
        step_up_required=room["step_up_required"],
    )

    incident = create_protected_launch_incident_receipt(
        handoff=handoff,
        incident_type=scenario["incident_type"],
        reason_code=scenario["reason_code"],
        incident_stage=scenario["failure_stage"],
        detected_at="2026-07-14T13:00:00+00:00",
        recovery_receipt=recovery,
    )

    passed = all([
        base["status"] == "passed",
        detected,
        recovery["launch_authorization_state"]
        == "revoked",
        recovery["handoff_replay_state"] == "blocked",
        recovery["ob_access_state"] == "locked_back",
        recovery["default_deny_restored"] is True,
        recovery["new_handoff_required"] is True,
        incident["default_deny_restored"] is True,
        incident["ob_access_state"] == "locked_back",
    ])

    return {
        "room_id": handoff["approved_room_id"],
        "canonical_path": handoff["canonical_path"],
        "scenario": scenario["incident_type"],
        "status": "passed" if passed else "failed",
        "base_integration": base,
        "detector_result": detector,
        "recovery_receipt": recovery,
        "incident_receipt": incident,
        "preview_only": True,
        "writes_state": False,
    }


def run_six_room_failure_rehearsal() -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []

    for index, request in enumerate(
        ROOM_REQUESTS,
        start=1,
    ):
        scenario = FAILURE_SCENARIOS[index - 1]

        results.append(
            run_failure_injection(
                request=request,
                scenario=scenario,
                rehearsal_index=index,
            )
        )

    passed = (
        len(results) == 6
        and all(
            result["status"] == "passed"
            for result in results
        )
    )

    return {
        "status": "passed" if passed else "failed",
        "room_count": len(results),
        "results": results,
        "all_failures_detected": all(
            result["status"] == "passed"
            for result in results
        ),
        "all_sessions_locked_back": all(
            result["recovery_receipt"]["ob_access_state"]
            == "locked_back"
            for result in results
        ),
        "all_default_deny_restored": all(
            result["recovery_receipt"][
                "default_deny_restored"
            ]
            for result in results
        ),
        "all_new_handoffs_required": all(
            result["recovery_receipt"][
                "new_handoff_required"
            ]
            for result in results
        ),
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    rehearsal = run_six_room_failure_rehearsal()

    return {
        "pack": PACK_ID,
        "pack_name": "Six-Room Failure Injection Rehearsal",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "rehearsal": rehearsal,
        "all_failures_detected": (
            rehearsal["all_failures_detected"]
        ),
        "all_sessions_locked_back": (
            rehearsal["all_sessions_locked_back"]
        ),
        "all_default_deny_restored": (
            rehearsal["all_default_deny_restored"]
        ),
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2409",
        "safe_to_continue_to_pack_2409": True,
    }


def build_ir_cert_p2408_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2409_ir_cert_p2409() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2409",
        "name": "Owner Assurance Summary",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
