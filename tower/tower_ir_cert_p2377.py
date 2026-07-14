"""
SEARCHABLE LABEL: TOWER_PACK_2377_TOWER_TO_OB_LAUNCH_HANDOFF

Pack 2377 — Tower-to-OB Launch Handoff
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any, Dict


PACK_ID = "2377"
ENDPOINT = "/tower/ir-cert-v2377.json"


def _hash_payload(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def create_ob_launch_handoff(
    *,
    owner_id: str,
    session_id: str,
    approved_room: Dict[str, Any],
    canonical_path: str,
    mode: str,
    step_up_reference: str | None,
    clearance_decision_reference: str,
    issued_at: str | None = None,
    ttl_seconds: int = 300,
) -> Dict[str, Any]:
    now = (
        datetime.fromisoformat(issued_at)
        if issued_at
        else datetime.now(timezone.utc)
    )

    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    expires = now + timedelta(seconds=ttl_seconds)

    seed = {
        "owner_id": owner_id,
        "session_id": session_id,
        "room_id": approved_room["room_id"],
        "canonical_path": canonical_path,
        "mode": mode,
        "issued_at": now.isoformat(),
    }

    handoff_id = (
        "oblaunch_"
        + _hash_payload(seed)[:24]
    )

    handoff = {
        "handoff_id": handoff_id,
        "owner_id": owner_id,
        "session_id": session_id,
        "approved_room_id": approved_room["room_id"],
        "approved_room_name": (
            approved_room["display_name"]
        ),
        "canonical_path": canonical_path,
        "mode": mode,
        "step_up_reference": step_up_reference,
        "clearance_decision_reference": (
            clearance_decision_reference
        ),
        "issued_at": now.isoformat(),
        "expires_at": expires.isoformat(),
        "replay_policy": "single_use_same_session",
        "authorization_state": "issued_preview",
        "safety_boundaries": {
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

    integrity_source = {
        key: value
        for key, value in handoff.items()
        if key != "integrity_hash"
    }

    handoff["integrity_hash"] = _hash_payload(
        integrity_source
    )

    return handoff


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    example = create_ob_launch_handoff(
        owner_id="owner_preview",
        session_id="session_preview",
        approved_room={
            "room_id": "ob_room_dashboard",
            "display_name": "Dashboard",
        },
        canonical_path="/dashboard",
        mode="paper",
        step_up_reference=None,
        clearance_decision_reference="obclr_preview",
        issued_at="2026-07-13T12:00:00+00:00",
    )

    return {
        "pack": PACK_ID,
        "pack_name": "Tower-to-OB Launch Handoff",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "handoff_example": example,
        "replay_policy": "single_use_same_session",
        "integrity_hash_required": True,
        "expiration_required": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2378",
        "safe_to_continue_to_pack_2378": True,
    }


def build_ir_cert_p2377_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2378_ir_cert_p2378() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2378",
        "name": "Room Access Receipt",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
