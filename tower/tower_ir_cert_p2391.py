"""
SEARCHABLE LABEL: TOWER_PACK_2391_ACTIVE_LAUNCH_LEDGER

Pack 2391 — Active Launch Authorization Ledger
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict, Iterable


PACK_ID = "2391"
ENDPOINT = "/tower/ir-cert-v2391.json"


def build_active_launch_ledger(
    *,
    issued_handoffs: Iterable[Dict[str, Any]],
    consumed_handoff_ids: Iterable[str],
    revoked_handoff_ids: Iterable[str],
    closed_handoff_ids: Iterable[str],
) -> Dict[str, Any]:
    consumed = set(consumed_handoff_ids)
    revoked = set(revoked_handoff_ids)
    closed = set(closed_handoff_ids)

    entries = []

    for handoff in issued_handoffs:
        handoff_id = handoff["handoff_id"]

        if handoff_id in revoked:
            state = "revoked"
        elif handoff_id in closed:
            state = "closed"
        elif handoff_id in consumed:
            state = "consumed"
        else:
            state = "active_preview"

        entries.append({
            "handoff_id": handoff_id,
            "owner_id": handoff["owner_id"],
            "session_id": handoff["session_id"],
            "room_id": handoff["approved_room_id"],
            "canonical_path": handoff["canonical_path"],
            "mode": handoff["mode"],
            "expires_at": handoff["expires_at"],
            "authorization_state": state,
            "single_use": True,
            "preview_only": True,
        })

    active = [
        entry
        for entry in entries
        if entry["authorization_state"] == "active_preview"
    ]

    return {
        "entry_count": len(entries),
        "active_count": len(active),
        "entries": entries,
        "active_entries": active,
        "default_deny_for_missing_handoff": True,
        "append_only_projection": True,
        "preview_only": True,
        "writes_state": False,
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": "Active Launch Authorization Ledger",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "ledger_states": [
            "active_preview",
            "consumed",
            "revoked",
            "closed",
        ],
        "single_use": True,
        "default_deny_for_missing_handoff": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2392",
        "safe_to_continue_to_pack_2392": True,
    }


def build_ir_cert_p2391_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2392_ir_cert_p2392() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2392",
        "name": "Launch Consume and Revoke Contract",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
