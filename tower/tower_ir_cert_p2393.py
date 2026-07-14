"""
SEARCHABLE LABEL: TOWER_PACK_2393_PROTECTED_ROUTE_ENFORCEMENT

Pack 2393 — Protected Route Enforcement Gate
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_ir_cert_p2384 import (
    validate_ob_launch_authorization,
)
from tower.tower_ir_cert_p2385 import (
    evaluate_handoff_replay_guard,
)
from tower.tower_ir_cert_p2386 import (
    evaluate_cross_room_scope,
)


PACK_ID = "2393"
ENDPOINT = "/tower/ir-cert-v2393.json"


def enforce_protected_ob_route(
    *,
    decision_envelope: Dict[str, Any],
    handoff: Dict[str, Any],
    owner_id: str,
    session_id: str,
    requested_room_id: str,
    requested_path: str,
    requested_mode: str,
    evaluation_time: str,
    consumed_handoff_ids: list[str],
    revoked_handoff_ids: list[str],
) -> Dict[str, Any]:
    launch = validate_ob_launch_authorization(
        decision_envelope=decision_envelope,
        handoff=handoff,
        owner_id=owner_id,
        session_id=session_id,
        requested_path=requested_path,
        requested_mode=requested_mode,
    )

    freshness = evaluate_handoff_replay_guard(
        handoff=handoff,
        evaluation_time=evaluation_time,
        consumed_handoff_ids=consumed_handoff_ids,
        revoked_handoff_ids=revoked_handoff_ids,
    )

    scope = evaluate_cross_room_scope(
        handoff=handoff,
        requested_room_id=requested_room_id,
        requested_path=requested_path,
        requested_mode=requested_mode,
        requested_session_id=session_id,
    )

    allowed = all([
        launch["allowed"],
        freshness["allowed"],
        scope["allowed"],
    ])

    if not launch["allowed"]:
        reason = launch["reason_code"]
    elif not freshness["allowed"]:
        reason = freshness["reason_code"]
    elif not scope["allowed"]:
        reason = scope["reason_code"]
    else:
        reason = "ob_protected_route_enforcement_allow"

    return {
        "allowed": allowed,
        "reason_code": reason,
        "handoff_id": handoff.get("handoff_id"),
        "room_id": requested_room_id,
        "canonical_path": requested_path,
        "launch_validation": launch,
        "freshness_validation": freshness,
        "scope_validation": scope,
        "default_deny": True,
        "ob_self_authorization": False,
        "preview_only": True,
        "writes_state": False,
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": "Protected Route Enforcement Gate",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "required_validations": [
            "launch_authorization",
            "handoff_freshness",
            "replay_state",
            "room_scope",
            "path_scope",
            "mode_scope",
            "session_scope",
        ],
        "default_deny": True,
        "ob_self_authorization": False,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2394",
        "safe_to_continue_to_pack_2394": True,
    }


def build_ir_cert_p2393_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2394_ir_cert_p2394() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2394",
        "name": "Authorization Denial Receipt",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
