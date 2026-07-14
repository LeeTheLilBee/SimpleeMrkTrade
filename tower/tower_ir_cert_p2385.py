"""
SEARCHABLE LABEL: TOWER_PACK_2385_HANDOFF_REPLAY_GUARD

Pack 2385 — Handoff Expiration and Replay Guard
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any, Dict, Iterable


PACK_ID = "2385"
ENDPOINT = "/tower/ir-cert-v2385.json"


def evaluate_handoff_replay_guard(
    *,
    handoff: Dict[str, Any],
    evaluation_time: str,
    consumed_handoff_ids: Iterable[str],
    revoked_handoff_ids: Iterable[str],
) -> Dict[str, Any]:
    now = datetime.fromisoformat(evaluation_time)
    expires = datetime.fromisoformat(
        handoff["expires_at"]
    )

    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)

    consumed = set(consumed_handoff_ids)
    revoked = set(revoked_handoff_ids)
    handoff_id = handoff["handoff_id"]

    if now >= expires:
        return {
            "allowed": False,
            "reason_code": "ob_launch_handoff_expired",
            "handoff_id": handoff_id,
            "preview_only": True,
            "writes_state": False,
        }

    if handoff_id in revoked:
        return {
            "allowed": False,
            "reason_code": "ob_launch_handoff_revoked",
            "handoff_id": handoff_id,
            "preview_only": True,
            "writes_state": False,
        }

    if handoff_id in consumed:
        return {
            "allowed": False,
            "reason_code": "ob_launch_handoff_replay_blocked",
            "handoff_id": handoff_id,
            "preview_only": True,
            "writes_state": False,
        }

    return {
        "allowed": True,
        "reason_code": "ob_launch_handoff_fresh",
        "handoff_id": handoff_id,
        "replay_policy": handoff["replay_policy"],
        "preview_only": True,
        "writes_state": False,
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": "Handoff Expiration and Replay Guard",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "expiration_required": True,
        "single_use_required": True,
        "revocation_check_required": True,
        "replay_reason_code": (
            "ob_launch_handoff_replay_blocked"
        ),
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2386",
        "safe_to_continue_to_pack_2386": True,
    }


def build_ir_cert_p2385_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2386_ir_cert_p2386() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2386",
        "name": "Cross-Room Session Scope Guard",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
