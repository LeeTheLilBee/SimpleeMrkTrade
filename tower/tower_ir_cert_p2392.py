"""
SEARCHABLE LABEL: TOWER_PACK_2392_LAUNCH_CONSUME_REVOKE

Pack 2392 — Launch Consume and Revoke Contract
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict


PACK_ID = "2392"
ENDPOINT = "/tower/ir-cert-v2392.json"


def _reference(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return "obauthstate_" + hashlib.sha256(
        encoded
    ).hexdigest()[:24]


def transition_launch_authorization(
    *,
    handoff_id: str,
    current_state: str,
    requested_action: str,
    reason_code: str,
    event_time: str,
) -> Dict[str, Any]:
    allowed_transitions = {
        "active_preview": {
            "consume": "consumed",
            "revoke": "revoked",
            "close": "closed",
        },
        "consumed": {
            "close": "closed",
            "revoke": "revoked",
        },
        "revoked": {},
        "closed": {},
    }

    target = allowed_transitions.get(
        current_state,
        {},
    ).get(requested_action)

    allowed = target is not None

    result = {
        "handoff_id": handoff_id,
        "current_state": current_state,
        "requested_action": requested_action,
        "allowed": allowed,
        "next_state": (
            target
            if allowed
            else current_state
        ),
        "reason_code": (
            reason_code
            if allowed
            else "ob_launch_state_transition_blocked"
        ),
        "event_time": event_time,
        "single_use_preserved": True,
        "preview_only": True,
        "writes_state": False,
    }

    result["state_transition_reference"] = _reference(
        result
    )

    return result


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": "Launch Consume and Revoke Contract",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "terminal_states": [
            "revoked",
            "closed",
        ],
        "replay_after_consume": False,
        "reactivation_after_revoke": False,
        "reactivation_after_close": False,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2393",
        "safe_to_continue_to_pack_2393": True,
    }


def build_ir_cert_p2392_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2393_ir_cert_p2393() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2393",
        "name": "Protected Route Enforcement Gate",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
