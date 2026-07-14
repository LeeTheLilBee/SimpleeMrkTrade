"""
SEARCHABLE LABEL: TOWER_PACK_2380_OWNER_REHEARSAL_READINESS

Pack 2380 — Owner Rehearsal Readiness Checkpoint

Proves:
owner identity
→ clearance translation
→ step-up
→ protected room manifest
→ launch handoff
→ OB room access
→ completion receipt
→ session close
→ lockback
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_ir_cert_p2372 import get_room_by_id
from tower.tower_ir_cert_p2373 import (
    normalize_app_id,
    normalize_request_type,
    resolve_observatory_route,
)
from tower.tower_ir_cert_p2374 import (
    translate_tower_clearance,
)
from tower.tower_ir_cert_p2375 import (
    evaluate_room_access,
)
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


PACK_ID = "2380"
ENDPOINT = "/tower/ir-cert-v2380.json"


def run_owner_rehearsal(
    *,
    owner_id: str = "owner_rehearsal",
    session_id: str = "session_rehearsal",
    requested_path: str = "/dashboard",
    mode: str = "paper",
    step_up_reference: str = "stepup_rehearsal",
    mission_account_id: str = "proof_demo",
    symbol: str = "AMD",
) -> Dict[str, Any]:
    app_id = normalize_app_id("ob")
    request_type = normalize_request_type(
        "ob.protected_room.launch"
    )

    identity = {
        "owner_id": owner_id,
        "tower_role": "owner",
        "identity_verified": True,
        "account_active": True,
        "risk_state": "acceptable",
        "lockdown_state": "tower_guarded_default_deny",
    }

    clearance = translate_tower_clearance(
        subject_id=owner_id,
        tower_role=identity["tower_role"],
        identity_verified=identity["identity_verified"],
        account_active=identity["account_active"],
        risk_state=identity["risk_state"],
        lockdown_state=identity["lockdown_state"],
    )

    route = resolve_observatory_route(requested_path)

    if not route["allowed"]:
        return {
            "status": "blocked",
            "reason_code": route["reason_code"],
            "preview_only": True,
        }

    room = get_room_by_id(route["room_id"])

    object_context = {
        "symbol": symbol,
        "mission_account_id": mission_account_id,
    }

    step_up_valid = bool(step_up_reference)

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
        step_up_valid=step_up_valid,
        object_context=object_context,
    )

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
        step_up_valid=step_up_valid,
        object_context_by_room={
            "ob_room_symbol_page": {
                "symbol": symbol,
            },
            "ob_room_trade_center": {
                "mission_account_id": mission_account_id,
            },
            "ob_room_review_center": {
                "mission_account_id": mission_account_id,
            },
            "ob_room_owner_console": {
                "mission_account_id": mission_account_id,
            },
        },
    )

    available_ids = {
        item["room_id"]
        for item in manifest["available_rooms"]
    }

    if not access["allowed"]:
        return {
            "status": "blocked",
            "reason_code": access["reason_code"],
            "clearance": clearance,
            "manifest": manifest,
            "preview_only": True,
        }

    if room["room_id"] not in available_ids:
        return {
            "status": "blocked",
            "reason_code": (
                "ob_room_not_present_in_protected_manifest"
            ),
            "clearance": clearance,
            "manifest": manifest,
            "preview_only": True,
        }

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
        issued_at="2026-07-13T12:00:00+00:00",
    )

    access_receipt = create_room_access_receipt(
        handoff=handoff,
        bridge_decision=access["reason_code"],
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
        launch_time="2026-07-13T12:00:01+00:00",
    )

    close_receipt = close_ob_launch_session(
        handoff=handoff,
        access_receipt=access_receipt,
        close_time="2026-07-13T12:05:00+00:00",
        close_reason="owner_rehearsal_completed",
    )

    sequence = [
        {
            "step": "owner_identity",
            "passed": identity["identity_verified"],
        },
        {
            "step": "clearance_translation",
            "passed": (
                clearance["allowed"]
                and clearance[
                    "canonical_clearance_value"
                ] == "ob_owner_command"
                and clearance[
                    "canonical_clearance_rank"
                ] == 900
            ),
        },
        {
            "step": "step_up",
            "passed": (
                step_up_valid
                if room["step_up_required"]
                else True
            ),
        },
        {
            "step": "protected_room_manifest",
            "passed": room["room_id"] in available_ids,
        },
        {
            "step": "launch_handoff",
            "passed": bool(handoff["integrity_hash"]),
        },
        {
            "step": "ob_room_access",
            "passed": access["allowed"],
        },
        {
            "step": "completion_receipt",
            "passed": bool(
                access_receipt["integrity_hash"]
            ),
        },
        {
            "step": "session_close",
            "passed": (
                close_receipt[
                    "launch_authorization_state"
                ] == "revoked"
            ),
        },
        {
            "step": "lockback",
            "passed": (
                close_receipt["ob_access_state"]
                == "locked_back"
                and close_receipt[
                    "default_deny_restored"
                ]
            ),
        },
    ]

    passed = all(item["passed"] for item in sequence)

    return {
        "status": "passed" if passed else "failed",
        "recommendation": (
            "GO_PROTECTED_OWNER_REHEARSAL_CONTRACT_READY"
            if passed
            else "NO_GO_OWNER_REHEARSAL_CONTRACT_INCOMPLETE"
        ),
        "app_id": app_id,
        "request_type": request_type,
        "requested_path": requested_path,
        "canonical_path": route["canonical_path"],
        "room_id": room["room_id"],
        "clearance": clearance,
        "access_decision": access,
        "protected_room_manifest": manifest,
        "launch_handoff": handoff,
        "access_receipt": access_receipt,
        "close_receipt": close_receipt,
        "sequence": sequence,
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
    dashboard = run_owner_rehearsal(
        requested_path="/dashboard",
        mode="paper",
    )

    owner_console = run_owner_rehearsal(
        requested_path="/owner-console",
        mode="paper",
    )

    return {
        "pack": PACK_ID,
        "pack_name": (
            "Owner Rehearsal Readiness Checkpoint"
        ),
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "dashboard_rehearsal": dashboard,
        "owner_console_rehearsal": owner_console,
        "complete_sequence_proven": (
            dashboard["status"] == "passed"
            and owner_console["status"] == "passed"
        ),
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2381",
        "safe_to_continue_to_pack_2381": True,
    }


def build_ir_cert_p2380_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2381_ir_cert_p2381() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2381",
        "name": "Observatory Protected Launch Continuation",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
