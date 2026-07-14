"""
SEARCHABLE LABEL: TOWER_PACK_2401_LAUNCH_STATE_PROJECTION

Pack 2401 — Launch State Projection Contract
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict, Iterable


PACK_ID = "2401"
ENDPOINT = "/tower/ir-cert-v2401.json"


VALID_STATES = {
    "issued_preview",
    "active_preview",
    "consumed",
    "revoked",
    "closed",
    "expired",
    "locked_back",
}


def project_launch_state(
    *,
    handoff: Dict[str, Any],
    transition_events: Iterable[Dict[str, Any]],
) -> Dict[str, Any]:
    current_state = handoff.get(
        "authorization_state",
        "issued_preview",
    )

    history = [{
        "event_type": "handoff_issued",
        "state": current_state,
        "reference": handoff.get("handoff_id"),
    }]

    transitions = {
        ("issued_preview", "activate"): "active_preview",
        ("active_preview", "consume"): "consumed",
        ("issued_preview", "revoke"): "revoked",
        ("active_preview", "revoke"): "revoked",
        ("consumed", "revoke"): "revoked",
        ("issued_preview", "expire"): "expired",
        ("active_preview", "expire"): "expired",
        ("consumed", "close"): "closed",
        ("active_preview", "close"): "closed",
        ("revoked", "lockback"): "locked_back",
        ("closed", "lockback"): "locked_back",
        ("expired", "lockback"): "locked_back",
    }

    blocked_events = []

    for event in transition_events:
        action = event.get("action")
        target = transitions.get((current_state, action))

        if target is None:
            blocked_events.append({
                "action": action,
                "from_state": current_state,
                "reason_code": (
                    "ob_launch_projection_transition_blocked"
                ),
            })
            continue

        current_state = target

        history.append({
            "event_type": action,
            "state": current_state,
            "reference": event.get("reference"),
        })

    return {
        "handoff_id": handoff.get("handoff_id"),
        "projected_state": current_state,
        "state_valid": current_state in VALID_STATES,
        "history": history,
        "blocked_events": blocked_events,
        "terminal": current_state in {
            "revoked",
            "closed",
            "expired",
            "locked_back",
        },
        "reusable": current_state in {
            "issued_preview",
            "active_preview",
        },
        "preview_only": True,
        "writes_state": False,
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": "Launch State Projection Contract",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "valid_states": sorted(VALID_STATES),
        "terminal_states": [
            "revoked",
            "closed",
            "expired",
            "locked_back",
        ],
        "state_reactivation_allowed": False,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2402",
        "safe_to_continue_to_pack_2402": True,
    }


def build_ir_cert_p2401_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2402_ir_cert_p2402() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2402",
        "name": "Step-Up Lifecycle Verification",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
