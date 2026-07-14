"""
SEARCHABLE LABEL: TOWER_PACK_2382_PACK_101_BRIDGE_ADAPTER

Pack 2382 — Pack 101 Bridge Adapter

Adapts Pack 101-style bridge requests into the canonical
Tower Observatory protected bridge request.
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict

from tower.tower_ir_cert_p2381 import (
    build_protected_bridge_request,
)


PACK_ID = "2382"
ENDPOINT = "/tower/ir-cert-v2382.json"

PACK_101_ACCEPTED_REQUESTS = {
    "canonical_observatory_bridge_request",
    "observatory_protected_room_request",
    "ob_room_launch_request",
}


def adapt_pack_101_bridge_request(
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    source_request_type = str(
        payload.get("bridge_request_type", "")
    ).strip()

    if source_request_type not in PACK_101_ACCEPTED_REQUESTS:
        return {
            "adapted": False,
            "reason_code": (
                "pack_101_bridge_request_type_unsupported"
            ),
            "source_request_type": source_request_type,
            "default_deny": True,
            "preview_only": True,
            "writes_state": False,
        }

    adapted = build_protected_bridge_request(
        request_id=str(payload.get("request_id", "")),
        requester_id=str(
            payload.get("owner_id")
            or payload.get("requester_id")
            or ""
        ),
        session_id=str(payload.get("session_id", "")),
        app_id=str(
            payload.get("app_id")
            or payload.get("target_app")
            or ""
        ),
        request_type=str(
            payload.get("request_type")
            or "ob.protected_room.launch"
        ),
        requested_path=str(
            payload.get("requested_path")
            or payload.get("preferred_route")
            or ""
        ),
        requested_mode=str(
            payload.get("mode")
            or payload.get("requested_mode")
            or ""
        ),
        tower_role=str(
            payload.get("tower_role")
            or payload.get("role")
            or ""
        ),
        object_context=deepcopy(
            payload.get("object_context") or {}
        ),
    )

    return {
        "adapted": adapted["valid"],
        "reason_code": (
            "pack_101_bridge_request_adapted"
            if adapted["valid"]
            else adapted["reason_code"]
        ),
        "source_request_type": source_request_type,
        "canonical_request": adapted,
        "default_deny": True,
        "preview_only": True,
        "writes_state": False,
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    example = adapt_pack_101_bridge_request({
        "bridge_request_type": (
            "canonical_observatory_bridge_request"
        ),
        "request_id": "pack101_preview",
        "owner_id": "owner_preview",
        "session_id": "session_preview",
        "app_id": "ob",
        "preferred_route": "/dashboard",
        "mode": "paper",
        "tower_role": "owner",
    })

    return {
        "pack": PACK_ID,
        "pack_name": "Pack 101 Bridge Adapter",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "accepted_pack_101_request_types": sorted(
            PACK_101_ACCEPTED_REQUESTS
        ),
        "preview_adapter_result": example,
        "ob_route_guessing_enabled": False,
        "default_deny": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2383",
        "safe_to_continue_to_pack_2383": True,
    }


def build_ir_cert_p2382_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2383_ir_cert_p2383() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2383",
        "name": "Tower Room Decision Envelope",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
